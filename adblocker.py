# -*- coding: utf-8 -*-
"""
adblocker.py — Tiny host-based adblocker with path hints.

Responsibilities:
- Maintain and periodically update blocklists from well-known sources.
- Persist the blocklist cache on disk.
- Expose TinyAdblockInterceptor for QWebEngine to use.
"""

import json
import re
import threading
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta

from qt_compat import (
    QtCore,
    QWebEngineUrlRequestInterceptor,
    QWebEngineUrlRequestInfo,
    UTC,
    vlog,
)

# ------------------ Blocklists ------------------
DEFAULT_LISTS = {
    # EasyList family
    "EasyList": "https://easylist.to/easylist/easylist.txt",
    "EasyPrivacy": "https://easylist.to/easylist/easyprivacy.txt",
    "Fanboy Annoyances": "https://easylist.to/easylist/fanboy-annoyance.txt",
    "Fanboy Social": "https://easylist-downloads.adblockplus.org/fanboy-social.txt",

    # uBO (correct branch: master)
    "uBO Privacy": "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/privacy.txt",
    "uBO Badware": "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/badware.txt",
    "uBO Resource abuse": "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/resource-abuse.txt",
    "uBO Annoyances": "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/annoyances.txt",
    "uBO Quick fixes": "https://raw.githubusercontent.com/uBlockOrigin/uAssets/master/filters/quick-fixes.txt",

    # AdGuard (ABP endpoints)
    "AdGuard Base": "https://filters.adtidy.org/extension/ublock/filters/2.txt",
    "AdGuard Tracking": "https://filters.adtidy.org/extension/ublock/filters/3.txt",
    "AdGuard URL Tracking": "https://filters.adtidy.org/extension/ublock/filters/17.txt",
    "AdGuard Annoyances": "https://filters.adtidy.org/extension/ublock/filters/14.txt",

    # OISD
    "OISD Basic": "https://abp.oisd.nl/basic/",

    # Security / hosts
    "NoCoin (anti-mining)": "https://raw.githubusercontent.com/hoshsadiq/adblock-nocoin-list/master/hosts.txt",
    "Phishing Army ext": "https://phishing.army/download/phishing_army_blocklist_extended.txt",

    # Hosts/domain-only sets
    "Peter Lowe": "https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext",
    "StevenBlack": "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts",
    "URLHaus Hosts": "https://urlhaus.abuse.ch/downloads/hostfile/",

    # HaGeZi curated
    "HaGeZi TIF (ABP)": "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/adblock/tif.txt",
    "HaGeZi Multi Light": "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/domains/light.txt",
    "HaGeZi Multi Pro": "https://raw.githubusercontent.com/hagezi/dns-blocklists/main/domains/pro.txt",
}

# Location of the JSON cache with hosts/path hints
CACHE_FILE = Path.home() / ".runit_qt_blockcache.json"

# Default path fragments that are usually ad/track endpoints
PATH_HINTS_DEFAULT = {
    "/ads", "/adserver", "/advert", "/banner",
    "/track", "/pixel", "/analytics", "/promotions", "/promo",
}

# Never block these (YouTube/CDNs/WordPress/assets)
ADBLOCK_ALLOW_SUFFIXES = {
    # YouTube/Google media/CDNs
    "youtube.com", "youtu.be", "googlevideo.com", "ytimg.com", "gstatic.com",
    "googleapis.com", "googleusercontent.com", "ggpht.com", "youtube-nocookie.com",
    # WordPress ecosystem & common assets
    "wp.com", "wordpress.com", "gravatar.com", "grvcdn.com", "jetpack.com", "s.w.org",
    # Popular CDNs / fonts / amp
    "cdn.jsdelivr.net", "cdnjs.cloudflare.com", "cloudflare.com", "cloudfront.net",
    "bootstrapcdn.com", "akamaihd.net", "akamaized.net",
    "fonts.googleapis.com", "fonts.gstatic.com", "ajax.googleapis.com",
    "cdn.ampproject.org", "ampproject.org",
}


# --------------- parsing helpers ---------------
def _normalize_domain(d: str) -> str:
    d = (d or "").strip().lower().lstrip(".")
    if d.startswith("www."):
        d = d[4:]
    return d


def _abp_domain(line: str):
    """Extract domain from ABP-style '||domain^' filter rules."""
    m = re.match(r"^\|\|([^\^/]+)\^", line)
    return _normalize_domain(m.group(1)) if m else None


def _hosts_domain(line: str):
    """Extract domain from hosts-file style lines."""
    m = re.match(r"^(?:0\.0\.0\.0|127\.0\.0\.1)\s+([^\s#]+)", line)
    if m:
        return _normalize_domain(m.group(1))
    m2 = re.match(r"^([a-z0-9\.\-]+\.[a-z]{2,})$", line)
    return _normalize_domain(m2.group(1)) if m2 else None


def _fetch_text(url: str, timeout: int = 30) -> str:
    """
    Fetch plain text from a URL, with a small fallback for GitHub's main/master
    branch naming differences.
    """
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "RunIT-QT/0.9 (+local) Python-urllib"},
    )
    try:
        return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")
    except urllib.error.HTTPError as e:
        if e.code == 404 and "raw.githubusercontent.com" in url:
            swapped = (
                url.replace("/main/", "/master/")
                if "/main/" in url
                else url.replace("/master/", "/main/")
            )
            return urllib.request.urlopen(
                urllib.request.Request(
                    swapped, headers={"User-Agent": "RunIT-QT/0.9"}
                ),
                timeout=timeout,
            ).read().decode("utf-8", "ignore")
        raise


# --------------- cache management ---------------
def update_blocklist(force: bool = False):
    """
    Update the blocklist cache in a background thread.

    - Downloads all configured filter lists (unless the cache is fresh).
    - Extracts domains and small URL fragments.
    - Persists them as JSON to CACHE_FILE.
    """
    try:
        if CACHE_FILE.exists() and not force:
            meta = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
            last = datetime.fromisoformat(meta.get("last_update"))
            if datetime.now(UTC) - last < timedelta(days=7):
                # Cache is still fresh; skip update.
                return
    except Exception:
        pass

    def worker():
        vlog("[Adblock] update start", "(force)" if force else "")
        hosts: set[str] = set()
        paths: set[str] = set(PATH_HINTS_DEFAULT)

        for name, url in DEFAULT_LISTS.items():
            try:
                data = _fetch_text(url, timeout=30)
                before = len(hosts)
                for raw in data.splitlines():
                    line = raw.strip()
                    if not line or line.startswith(("!", "[Adblock", "#")):
                        continue

                    d = _abp_domain(line) or _hosts_domain(line)
                    if d:
                        hosts.add(d)
                        continue

                    if "/" in line and not line.startswith(("@@", "##", "#@")):
                        frag = line.replace("*", "").lower()
                        if 3 <= len(frag) <= 64 and "/" in frag:
                            paths.add(frag.split("$", 1)[0])
                vlog(f"[Adblock] {name}: +{len(hosts) - before} hosts (total {len(hosts)})")
            except Exception as e:
                vlog(f"[Adblock] Failed {name}: {e}")

        try:
            CACHE_FILE.write_text(
                json.dumps(
                    {
                        "last_update": datetime.now(UTC).isoformat(),
                        "hosts": sorted(list(hosts)),
                        "paths": sorted(list(paths))[:1024],
                    }
                ),
                encoding="utf-8",
            )
            vlog(
                f"[Adblock] Cache saved: hosts={len(hosts)}, paths={min(len(paths), 1024)}"
            )
        except Exception as e:
            vlog("[Adblock] cache save error:", e)

    threading.Thread(target=worker, daemon=True).start()


def load_blocklist():
    """
    Load blocklist from CACHE_FILE.

    Returns:
        (blocked_hosts: set[str], blocked_paths: set[str])
    """
    if not CACHE_FILE.exists():
        update_blocklist(force=True)
        return set(), set(PATH_HINTS_DEFAULT)
    try:
        meta = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        return set(meta.get("hosts", [])), set(meta.get("paths", PATH_HINTS_DEFAULT))
    except Exception:
        return set(), set(PATH_HINTS_DEFAULT)


# --------------- Tiny interceptor ---------------
class TinyAdblockInterceptor(QWebEngineUrlRequestInterceptor):
    """
    Host-only blocker + tiny path hints.

    Design goals:
    - Never blocks stylesheets or fonts to avoid blank pages.
    - Avoids blocking popular media/CDN domains via suffix allow-lists.
    - Keeps memory footprint small by using only hosts and short path fragments.
    """

    def __init__(
        self,
        blocked_hosts: set[str],
        blocked_paths: set[str],
        allow_suffixes: set[str] | None = None,
    ):
        super().__init__()
        self.blocked_hosts = blocked_hosts
        self.blocked_paths = blocked_paths
        self.allow_suffixes = set(allow_suffixes or set())
        self.enabled = True
        # Per-site allow-list (suffix-based) toggled from the UI
        self.site_allow_suffixes: set[str] = set()

    # --- small helpers ---
    @staticmethod
    def _host_in(blocked: set[str], host: str) -> bool:
        """
        Return True if 'host' or any of its parent domains is in 'blocked'.
        Example: ads.example.com -> checks ads.example.com, example.com, com.
        """
        h = (host or "").lower().strip(".")
        if not h:
            return False
        while True:
            if h in blocked:
                return True
            i = h.find(".")
            if i == -1:
                break
            h = h[i + 1 :]
        return False

    def _is_allowed_by_suffix(self, host: str) -> bool:
        """
        Return True if the host matches a globally or per-site allow-listed suffix.
        """
        h = (host or "").lower().strip(".")
        for s in (self.allow_suffixes | self.site_allow_suffixes):
            if h == s or h.endswith("." + s):
                return True
        return False

    @staticmethod
    def _rt(info, name, default=None):
        """
        Cross-version safe access to QWebEngineUrlRequestInfo.ResourceType enums.
        """
        try:
            return getattr(QWebEngineUrlRequestInfo, name)
        except Exception:
            enum = getattr(QWebEngineUrlRequestInfo, "ResourceType", None)
            return getattr(enum, name, default) if enum else default

    # --- main interception logic ---
    def interceptRequest(self, info: QWebEngineUrlRequestInfo):
        """
        Called by QWebEngine for each request.

        We:
        - Never block when disabled.
        - Never block the main frame.
        - Never block stylesheets & fonts.
        - Apply domain + simple path matching for subresources.
        """
        try:
            if not self.enabled:
                return

            url = info.requestUrl()
            host = (url.host() or "").lower()
            path = (url.path() or "").lower()

            # Never block allow-listed CDNs or per-site allowed suffixes
            if self._is_allowed_by_suffix(host):
                return

            rt = info.resourceType()
            rt_main = self._rt(info, "ResourceTypeMainFrame", 0)
            rt_css = self._rt(info, "ResourceTypeStylesheet", -1)
            rt_font = self._rt(info, "ResourceTypeFontResource", -2)

            # Never block stylesheets or fonts (prevents "white page with links")
            if rt in (rt_css, rt_font) or path.endswith(
                (".css", ".woff", ".woff2", ".ttf", ".otf", ".eot", ".svg")
            ):
                return

            # Main frame is allowed
            if rt == rt_main:
                return

            # Host-level block for subresources only
            if self._host_in(self.blocked_hosts, host):
                info.block(True)
                return

            # Light path hints
            for needle in self.blocked_paths:
                if needle in path:
                    info.block(True)
                    return
        except Exception:
            # Fail open on any unexpected error.
            pass
