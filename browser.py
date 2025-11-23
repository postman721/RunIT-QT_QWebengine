# -*- coding: utf-8 -*-
"""
browser.py — Main Browser window implementation.

This module contains the Browser QMainWindow with:
- Two-row toolbar: navigation + tools/search/zoom.
- Tabbed browsing with last-tab protection.
- Adblock controls (global + per-site).
- JS/Images toggle.
- Zoom controls and shortcuts.
- Session restore/save.
- HTTPS lock icon and certificate viewer.
- Download handling with a safety prompt for risky types.
"""

import json
import os
import re
import sys
import threading

from pathlib import Path

from qt_compat import (
    Qt,
    QtCore,
    QtGui,
    QUrl,
    QSize,
    QKeySequence,
    QAction,
    QApplication,
    QMainWindow,
    QToolBar,
    QToolButton,
    QLineEdit,
    QTabWidget,
    QStatusBar,
    QSizePolicy,
    QMessageBox,
    QWebEngineView,
    QtNetwork,
    CURSOR,
    vlog,
)
from config import APP_NAME, HOME_URL, FUTURE_QSS
from adblocker import (
    TinyAdblockInterceptor,
    update_blocklist,
    load_blocklist,
    ADBLOCK_ALLOW_SUFFIXES,
    CACHE_FILE,
)
from web_profile import build_lean_profile
from web_page import SecurePage


# ------------------ misc helpers ------------------
def is_url(text: str) -> bool:
    """
    Cheap URL heuristic. Accepts bare domains or http(s) URLs.
    """
    if not text:
        return False
    return re.match(
        r"^(https?://)?([-\w]+\.)+[\w-]{2,}(?:/[^ \n]*)?$",
        text.strip(),
    ) is not None


def as_http_url_or_search(text: str) -> str:
    """
    Interpret user input as URL or search query.

    - If it looks like a URL, ensure https:// is added.
    - Otherwise, send it to Startpage search.
    """
    t = text.strip()
    if t.startswith(("http://", "https://")):
        return t
    if is_url(t):
        return "https://" + t
    enc = QtCore.QUrl.toPercentEncoding(t)
    q = bytes(enc).decode("utf-8")
    return f"https://startpage.com/do/search?query={q}"


# ------------------ Browser ------------------
class Browser(QMainWindow):
    """
    Main browser window for RunIT-QT.

    High-level behavior:
    - Creates a lean QWebEngineProfile + TinyAdblockInterceptor.
    - Wires default toolbars, address bar, mini search box, and zoom controls.
    - Manages tabs and session persistence.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle(APP_NAME)
        self.resize(1600, 1200)

        # Apply global stylesheet/theme
        self.setStyleSheet(FUTURE_QSS)

        # Shared profile for all tabs/views
        self.profile = build_lean_profile()

        # Adblock: start background update + load cached rules
        update_blocklist()
        hosts, paths = load_blocklist()
        self.adblock = TinyAdblockInterceptor(hosts, paths, ADBLOCK_ALLOW_SUFFIXES)
        try:
            self.profile.setUrlRequestInterceptor(self.adblock)
        except Exception:
            # Older PyQt versions
            try:
                self.profile.setRequestInterceptor(self.adblock)
            except Exception:
                pass

        self._jsimg_enabled = True
        self._in_fullscreen = False

        # Path to session file (list of open URLs)
        self._session_file = os.path.join(os.path.expanduser("~"), ".runit_qt_session.json")

        # Build UI and restore previous session
        self._setup_ui()
        self.add_new_tab(QUrl(HOME_URL), "Home")
        self._restore_session()
        self.show()

    # ---------- UI wiring ----------
    def _setup_ui(self):
        """
        Create main tab widget, toolbars, shortcuts, and download hooks.
        """
        self.browser_tabs = QTabWidget(self)
        self.browser_tabs.setDocumentMode(True)
        self.browser_tabs.setMovable(True)
        self.browser_tabs.setTabsClosable(True)
        self.browser_tabs.tabCloseRequested.connect(self.close_tab)

        # Double-click tab bar -> new tab
        try:
            self.browser_tabs.tabBarDoubleClicked.connect(
                lambda _i: self.add_new_tab(QUrl("about:config"), "New Tab")
            )
        except Exception:
            pass

        self.setCentralWidget(self.browser_tabs)

        # Status bar for transient messages (zoom etc.)
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)

        # --- Row 1: primary navigation + address bar ---
        nav_top = QToolBar("Navigation", self)
        nav_top.setIconSize(QSize(24, 24))
        nav_top.setMovable(False)
        nav_top.setToolButtonStyle(
            getattr(Qt, "ToolButtonTextOnly", getattr(Qt.ToolButtonStyle, "ToolButtonTextOnly"))
        )
        self.addToolBar(nav_top)

        # Force next toolbar onto a new row
        try:
            self.addToolBarBreak()
        except Exception:
            pass

        # --- Row 2: page tools, search, zoom ---
        nav_bottom = QToolBar("Page Tools", self)
        nav_bottom.setIconSize(QSize(24, 24))
        nav_bottom.setMovable(False)
        nav_bottom.setToolButtonStyle(
            getattr(Qt, "ToolButtonTextOnly", getattr(Qt.ToolButtonStyle, "ToolButtonTextOnly"))
        )
        self.addToolBar(nav_bottom)

        def btn(text, tip, slot):
            """
            Helper to create uniform QToolButton with text and tooltip.
            """
            b = QToolButton(self)
            b.setText(text)
            b.setToolTip(tip or text)
            b.setMinimumWidth(96)
            b.clicked.connect(slot)
            return b

        # --- Top row content ---

        # New Tab
        nav_top.addWidget(
            btn("New Tab", "Open new tab", lambda: self.add_new_tab(QUrl("about:config"), "New Tab"))
        )

        # Back / Forward
        nav_top.addWidget(
            btn("Back", "Back", lambda: self.current_tab() and self.current_tab().back())
        )

        # URL bar
        self.urlbar = QLineEdit(self)
        self.urlbar.setPlaceholderText("Enter URL or search")
        self.urlbar.returnPressed.connect(self._go_url)

        # Make the URL bar expanding and wide
        try:
            Policy = getattr(QSizePolicy, "Policy", QSizePolicy)
            self.urlbar.setSizePolicy(
                getattr(Policy, "Expanding", QSizePolicy.Expanding),
                getattr(Policy, "Preferred", QSizePolicy.Preferred),
            )
        except Exception:
            try:
                self.urlbar.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            except Exception:
                pass
        self.urlbar.setMinimumWidth(900)
        nav_top.addWidget(self.urlbar)

        # Security lock indicator
        self.lock_btn = QToolButton(self)
        self.lock_btn.setText("🔓")
        self.lock_btn.setStyleSheet("font-size:20px;padding:0 8px;border:none;")
        self.lock_btn.setCursor(QtGui.QCursor(CURSOR("PointingHandCursor")))
        self.lock_btn.setToolTip("Connection security")
        self.lock_btn.clicked.connect(self._show_certificate)
        nav_top.addWidget(self.lock_btn)

        nav_top.addWidget(
            btn("Fwd", "Forward", lambda: self.current_tab() and self.current_tab().forward())
        )
        nav_top.addWidget(
            btn("Reload", "Reload", lambda: self.current_tab() and self.current_tab().reload())
        )
        nav_top.addWidget(btn("Home", "Home", self.navigate_home))

        # --- Bottom row content ---

        # Adblock global toggle
        self.adb_btn = btn("Adblock ON", "Toggle adblock (global)", self.toggle_adblock_global)
        nav_bottom.addWidget(self.adb_btn)
        self._refresh_adblock_btn()

        # Per-site adblock allow
        self.adb_site_btn = btn(
            "Allow this site", "Whitelist current site's suffix", self.toggle_adblock_site
        )
        nav_bottom.addWidget(self.adb_site_btn)

        # Mini search engine selector (gs/wiki/tube)
        self.switch_2 = QLineEdit(self)
        self.switch_2.setPlaceholderText("gs / wiki / tube")
        self.switch_2.setFixedWidth(110)
        self.switch_2.returnPressed.connect(self._extra_search)
        nav_bottom.addWidget(self.switch_2)

        # Search query box
        self.search_box = QLineEdit(self)
        self.search_box.setPlaceholderText("Search")
        self.search_box.setFixedWidth(160)
        self.search_box.returnPressed.connect(self._extra_search)
        nav_bottom.addWidget(self.search_box)

        # Adblock "update lists" button
        nav_bottom.addWidget(
            btn("Update Lists", "Force adblock update", self.force_update_lists)
        )

        # JS/Images toggle
        self.jsimg_btn = btn("JS/Img ON", "Toggle JavaScript & images", self.toggle_js_images)
        nav_bottom.addWidget(self.jsimg_btn)

        # Zoom controls
        nav_bottom.addWidget(
            btn("Zoom -", "Zoom out (Ctrl+-)", lambda: self.zoom_by(-0.1))
        )
        nav_bottom.addWidget(btn("100%", "Reset zoom (Ctrl+0)", self.zoom_reset))
        nav_bottom.addWidget(
            btn("Zoom +", "Zoom in (Ctrl+=)", lambda: self.zoom_by(+0.1))
        )

        # ------------- keyboard shortcuts -------------

        # New tab
        new_tab_act = QAction("New Tab", self)
        new_tab_act.setShortcut(QKeySequence("Ctrl+T"))
        new_tab_act.triggered.connect(
            lambda: self.add_new_tab(QUrl("about:config"), "New Tab")
        )
        self.addAction(new_tab_act)

        # Focus the bottom search field
        focus_search = QAction("Focus Search", self)
        focus_search.setShortcut(QKeySequence("Ctrl+K"))
        focus_search.triggered.connect(
            lambda: (self.search_box.setFocus(), self.search_box.selectAll())
        )
        self.addAction(focus_search)

        # Zoom shortcuts
        zoom_in_act = QAction("Zoom In", self)
        try:
            zoom_in_act.setShortcuts([QKeySequence("Ctrl++"), QKeySequence("Ctrl+=")])
        except Exception:
            zoom_in_act.setShortcut(QKeySequence("Ctrl+="))

        zoom_out_act = QAction("Zoom Out", self)
        zoom_out_act.setShortcut(QKeySequence("Ctrl+-"))

        zoom_reset_act = QAction("Reset Zoom", self)
        zoom_reset_act.setShortcut(QKeySequence("Ctrl+0"))

        zoom_in_act.triggered.connect(lambda: self.zoom_by(+0.1))
        zoom_out_act.triggered.connect(lambda: self.zoom_by(-0.1))
        zoom_reset_act.triggered.connect(self.zoom_reset)

        self.addAction(zoom_in_act)
        self.addAction(zoom_out_act)
        self.addAction(zoom_reset_act)

        # Download hook from QWebEngineProfile
        self.profile.downloadRequested.connect(self.on_download_requested)

    # ---------- JS & images ----------
    def _apply_jsimg_to_settings(self, settings_obj, enabled: bool):
        from qt_compat import _set_web_attr  # local import to avoid clutter

        _set_web_attr(settings_obj, "JavascriptEnabled", enabled)
        _set_web_attr(settings_obj, "AutoLoadImages", enabled)

    def toggle_js_images(self):
        """
        Toggle JavaScript and auto-loading images for all tabs and the profile.
        """
        self._jsimg_enabled = not self._jsimg_enabled
        enabled = self._jsimg_enabled

        self._apply_jsimg_to_settings(self.profile.settings(), enabled)

        for i in range(self.browser_tabs.count()):
            w = self.browser_tabs.widget(i)
            if isinstance(w, QWebEngineView):
                self._apply_jsimg_to_settings(w.settings(), enabled)
                try:
                    self._apply_jsimg_to_settings(w.page().settings(), enabled)
                except Exception:
                    pass

        self.jsimg_btn.setText("JS/Img ON" if enabled else "JS/Img OFF")
        self.status.showMessage(
            f"JavaScript & images {'ENABLED' if enabled else 'DISABLED'}",
            2000,
        )

    # ---------- Zoom ----------
    def zoom_by(self, delta: float, min_f: float = 0.25, max_f: float = 3.0):
        """
        Change zoom factor of current tab by 'delta'.
        """
        v = self.current_tab()
        if not v:
            return
        try:
            f = v.zoomFactor()
        except Exception:
            f = 1.0

        f = max(min(f + delta, max_f), min_f)

        try:
            v.setZoomFactor(f)
        except Exception:
            pass

        try:
            self.status.showMessage(f"Zoom: {int(round(f * 100))}%", 1500)
        except Exception:
            pass

    def zoom_reset(self):
        """
        Reset zoom factor to 100%.
        """
        v = self.current_tab()
        if not v:
            return
        try:
            v.setZoomFactor(1.0)
            self.status.showMessage("Zoom: 100%", 1500)
        except Exception:
            pass

    # ---------- Tabs ----------
    def close_tab(self, index: int):
        """
        Close tab at 'index' but keep at least one tab open (last-tab guard).
        """
        if self.browser_tabs.count() <= 1:
            # Last tab: don't close, just navigate to about:config.
            w = self.browser_tabs.currentWidget()
            if isinstance(w, QWebEngineView):
                w.setUrl(QUrl("about:config"))
            return
        self.browser_tabs.removeTab(index)

    def add_new_tab(self, qurl, label="New Tab"):
        """
        Create a new tab with a QWebEngineView + SecurePage and load 'qurl'.
        """
        view = QWebEngineView(self.browser_tabs)
        page = SecurePage(self.profile, view, lock_cb=self._set_lock)
        view.setPage(page)

        # Per-view settings: always start with JS/images enabled
        self._apply_jsimg_to_settings(view.settings(), True)
        try:
            self._apply_jsimg_to_settings(page.settings(), True)
        except Exception:
            pass

        # HTML5 fullscreen handling (YouTube etc.)
        try:
            page.fullScreenRequested.connect(self._on_fullscreen_requested)
        except Exception:
            pass

        view.urlChanged.connect(self._on_url_changed)
        view.titleChanged.connect(
            lambda title, v=view: self._update_tab_title_for(v, title)
        )

        idx = self.browser_tabs.addTab(view, label or "New Tab")
        self.browser_tabs.setCurrentIndex(idx)

        if not isinstance(qurl, QUrl):
            qurl = QUrl(str(qurl))
        view.setUrl(qurl)

        self._set_lock((qurl.scheme() or "").lower() == "https")
        self.urlbar.setFocus()
        self.urlbar.selectAll()

    def current_tab(self):
        """Return the current QWebEngineView or None."""
        w = self.browser_tabs.currentWidget()
        return w if isinstance(w, QWebEngineView) else None

    def _update_tab_title_for(self, view, title: str):
        """Update the tab text when the page title changes."""
        i = self.browser_tabs.indexOf(view)
        if i >= 0:
            self.browser_tabs.setTabText(i, title or "Loading…")

    # ---------- Fullscreen bridge ----------
    def _on_fullscreen_requested(self, request):
        """
        Handle HTML5 fullscreen requests from QWebEnginePage.
        """
        try:
            if request.toggleOn():
                self._enter_fullscreen()
            else:
                self._exit_fullscreen()
            request.accept()
        except Exception:
            try:
                request.reject()
            except Exception:
                pass

    def _enter_fullscreen(self):
        """
        Enter full-screen mode: hide toolbars/status and bind Esc to exit.
        """
        if self._in_fullscreen:
            return
        self._in_fullscreen = True

        # Save and hide all toolbars
        self._saved_toolbars = [
            (tb, tb.isVisible()) for tb in self.findChildren(QToolBar)
        ]
        for tb, was in self._saved_toolbars:
            tb.hide()

        self._saved_status_visible = self.status.isVisible() if hasattr(
            self, "status"
        ) else False
        if hasattr(self, "status"):
            self.status.hide()

        self.showFullScreen()

        # ESC to exit fullscreen
        self._esc_action = QAction(self)
        try:
            self._esc_action.setShortcut(QKeySequence(getattr(Qt, "Key_Escape")))
        except Exception:
            self._esc_action.setShortcut(QKeySequence("Escape"))
        self._esc_action.triggered.connect(self._exit_fullscreen)
        self.addAction(self._esc_action)

    def _exit_fullscreen(self):
        """
        Leave full-screen and restore visibility of UI elements.
        """
        if not self._in_fullscreen:
            return
        self._in_fullscreen = False

        self.showNormal()

        for tb, was in getattr(self, "_saved_toolbars", []):
            tb.setVisible(was)

        if hasattr(self, "status"):
            self.status.setVisible(getattr(self, "_saved_status_visible", True))

        if hasattr(self, "_esc_action"):
            try:
                self.removeAction(self._esc_action)
            except Exception:
                pass
            del self._esc_action

    # ---------- Navigation ----------
    def _go_url(self):
        """
        Called when the user presses Enter in the URL bar.
        """
        t = (self.urlbar.text() or "").strip()
        if not t:
            return
        self.current_tab().setUrl(QUrl(as_http_url_or_search(t)))

    def navigate_home(self):
        """
        Go to the configured home page.
        """
        tab = self.current_tab()
        if tab:
            tab.setUrl(QUrl(HOME_URL))

    def _on_url_changed(self, qurl):
        """
        Sync URL bar and lock icon when the current tab's URL changes.
        """
        if self.sender() is not self.current_tab():
            return
        self.urlbar.setText(qurl.toString())
        self._set_lock((qurl.scheme() or "").lower() == "https")

    # ---------- Search helpers ----------
    def _engine_url(self, engine_code: str, query: str) -> str:
        """
        Build search URL for mini-search engines ('gs', 'wiki', 'tube', ...).
        """
        q = bytes(QtCore.QUrl.toPercentEncoding(query or "")).decode("utf-8")
        e = (engine_code or "gs").lower().strip()
        if e in ("gs", "start", "sp"):
            return f"https://startpage.com/do/search?query={q}"
        if e in ("wiki", "wikipedia"):
            return (
                "https://en.wikipedia.org/w/index.php"
                f"?title=Special:Search&fulltext=Search&search={q}"
            )
        if e in ("tube", "yt", "youtube"):
            return f"https://www.youtube.com/results?search_query={q}"
        return f"https://startpage.com/do/search?query={q}"

    def _extra_search(self):
        """
        Triggered by the mini-search inputs (engine + query).
        """
        engine = (self.switch_2.text() or "gs").strip()
        query = (self.search_box.text() or "").strip()
        if not query:
            self.search_box.setFocus()
            self.search_box.selectAll()
            return

        target = self._engine_url(engine, query)
        if (tab := self.current_tab()) is not None:
            tab.setUrl(QUrl(target))
        self.status.showMessage(f"Searching '{query}' via {engine}", 2500)

    # ---------- Adblock toggles / refresh ----------
    def _refresh_adblock_btn(self):
        """
        Sync Adblock button label/tooltip with current interceptor state.
        """
        try:
            is_on = bool(getattr(self.adblock, "enabled", True))
        except Exception:
            is_on = True
        if hasattr(self, "adb_btn"):
            self.adb_btn.setText("Adblock ON" if is_on else "Adblock OFF")
            self.adb_btn.setToolTip(
                "Toggle adblock (currently ON)"
                if is_on
                else "Toggle adblock (currently OFF)"
            )

    def toggle_adblock_global(self):
        """
        Enable/disable adblocking globally and reload the current tab.
        """
        self.adblock.enabled = not self.adblock.enabled
        self._refresh_adblock_btn()
        self.status.showMessage(
            f"Adblock {'ENABLED' if self.adblock.enabled else 'DISABLED'}",
            2000,
        )
        if self.current_tab():
            self.current_tab().reload()

    def toggle_adblock_site(self):
        """
        Add/remove the current site's registrable suffix to/from the allow-list,
        then reload the current tab.
        """
        tab = self.current_tab()
        if not tab:
            return
        host = (tab.url().host() or "").lower().strip(".")
        if not host:
            return

        parts = host.split(".")
        suffix = ".".join(parts[-2:]) if len(parts) >= 2 else host

        if suffix in self.adblock.site_allow_suffixes:
            self.adblock.site_allow_suffixes.discard(suffix)
            self.status.showMessage(f"Removed site allow: {suffix}", 2500)
        else:
            self.adblock.site_allow_suffixes.add(suffix)
            self.status.showMessage(f"Allowed site: {suffix}", 2500)

        if self.current_tab():
            self.current_tab().reload()

    def _refresh_adblock_sets(self):
        """
        Reload hosts/path hints from cache after an update.
        """
        try:
            hosts, paths = load_blocklist()
            self.adblock.blocked_hosts = hosts
            self.adblock.blocked_paths = paths
            self.status.showMessage(
                f"Adblock: {len(hosts)} hosts, {len(paths)} hints", 5000
            )
            vlog("[Adblock] reloaded:", f"hosts={len(hosts)} paths={len(paths)}")
        except Exception as e:
            self.status.showMessage(f"Adblock reload failed: {e}", 5000)
            print("[Adblock] reload failed:", e, file=sys.stderr, flush=True)

    def force_update_lists(self):
        """
        Start a forced blocklist update and refresh local sets when it finishes.
        """
        self.status.showMessage("Updating adblock lists…", 4000)
        vlog("[UI] Update Lists clicked")

        try:
            before_mtime = CACHE_FILE.stat().st_mtime
        except Exception:
            before_mtime = 0.0

        def worker():
            vlog("[worker] update_blocklist(force=True)")
            update_blocklist(force=True)
            import time

            # Poll cache file for changes for up to ~20 seconds
            for i in range(80):
                time.sleep(0.25)
                try:
                    if CACHE_FILE.exists() and CACHE_FILE.stat().st_mtime > before_mtime:
                        vlog(f"[worker] cache changed after {0.25 * (i + 1):.2f}s")
                        break
                except Exception:
                    pass

            QtCore.QTimer.singleShot(0, self._refresh_adblock_sets)

        threading.Thread(target=worker, daemon=True).start()

    # ---------- Security / lock / certificate ----------
    def _set_lock(self, secure: bool):
        """
        Update lock icon to show secure/insecure state.
        """
        self.lock_btn.setText("🔒" if secure else "🔓")
        self.lock_btn.setToolTip("Secure HTTPS" if secure else "Not secure")

    def _show_certificate(self):
        """
        Perform a HEAD request and display basic certificate information.
        """
        tab = self.current_tab()
        if not tab:
            return
        url = tab.url()
        if (url.scheme() or "").lower() != "https":
            QMessageBox.information(self, "Certificate", "This page is not HTTPS.")
            return

        mgr = QtNetwork.QNetworkAccessManager(self)
        reply = mgr.head(QtNetwork.QNetworkRequest(url))
        loop = QtCore.QEventLoop()
        timer = QtCore.QTimer(self)
        timer.setSingleShot(True)

        def quit_loop():
            if loop.isRunning():
                loop.quit()

        timer.timeout.connect(quit_loop)
        reply.finished.connect(quit_loop)
        timer.start(8000)
        loop.exec()
        timer.stop()

        try:
            conf = reply.sslConfiguration()
        except Exception:
            conf = None

        reply.deleteLater()
        mgr.deleteLater()

        if not conf:
            QMessageBox.warning(self, "Certificate", "Could not retrieve certificate.")
            return

        try:
            chain = conf.peerCertificateChain()
        except Exception:
            chain = []

        if not chain:
            QMessageBox.warning(self, "Certificate", "No peer certificate chain provided.")
            return

        leaf = chain[0]
        try:
            SI = getattr(QtNetwork.QSslCertificate, "SubjectInfo", None)
            subj = leaf.subjectInfo(
                SI.CommonName if SI else QtNetwork.QSslCertificate.CommonName
            )
            issr = leaf.issuerInfo(
                SI.CommonName if SI else QtNetwork.QSslCertificate.CommonName
            )
            subj = (
                subj[0]
                if isinstance(subj, (list, tuple)) and subj
                else str(subj)
            )
            issr = (
                issr[0]
                if isinstance(issr, (list, tuple)) and issr
                else str(issr)
            )
            nb = leaf.effectiveDate().toString("yyyy-MM-dd HH:mm:ss t")
            na = leaf.expiryDate().toString("yyyy-MM-dd HH:mm:ss t")
        except Exception:
            subj = issr = ""
            nb = na = ""

        info = (
            f"Subject (CN): {subj}\n"
            f"Issuer (CN): {issr}\n"
            f"Valid From: {nb}\n"
            f"Valid Until: {na}\n"
        )
        QMessageBox.information(self, "Certificate Info", info)

    # ---------- Downloads ----------
    def _safe_name_hint(self, url_str: str) -> str:
        """
        Derive a filesystem-safe filename from a URL path.
        """
        try:
            name = re.split(r"[?#]", url_str.split("/")[-1])[0]
            name = re.sub(r"[^a-zA-Z0-9._-]+", "_", name).strip("._-")
            return name or "download.bin"
        except Exception:
            return "download.bin"

    def on_download_requested(self, item):
        """
        Intercept downloads to:
        - Show a safety warning on executable-like files.
        - Delegate actual saving to the DownloadDialog from download.py.
        """
        # Cancel the default download handling
        try:
            item.cancel()
        except Exception:
            pass

        url = item.url() if item else None
        url_str = url.toString() if url else ""
        hint = self._safe_name_hint(url_str)

        risky = (".exe", ".bat", ".cmd", ".scr", ".js", ".vbs", ".jar", ".apk", ".msi", ".dll")
        if any(hint.lower().endswith(ext) for ext in risky):
            r = QMessageBox.warning(
                self,
                "Potentially risky file type",
                (
                    "You’re about to download:\n\n"
                    f"  {hint}\n\n"
                    "This file type can run code on your system.\n"
                    "Do you want to continue?"
                ),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if r != QMessageBox.Yes:
                return

        # Delegate to your existing DownloadDialog
        from download import DownloadDialog

        DownloadDialog.download_url(self, url_str)

    # ---------- Session ----------
    def _restore_session(self):
        """
        Restore previously open tabs from ~/.runit_qt_session.json if present.
        """
        try:
            if os.path.exists(self._session_file):
                urls = json.load(
                    open(self._session_file, "r", encoding="utf-8")
                )
                if urls:
                    while self.browser_tabs.count():
                        self.browser_tabs.removeTab(0)
                    for u in urls:
                        self.add_new_tab(QUrl(u), "Restored")
        except Exception:
            pass

    def closeEvent(self, e):
        """
        Save the current session and dispose WebEngine pages cleanly on exit.
        """
        # Save session URLs
        try:
            urls = [
                self.browser_tabs.widget(i).url().toString()
                for i in range(self.browser_tabs.count())
                if isinstance(self.browser_tabs.widget(i), QWebEngineView)
            ]
            json.dump(urls, open(self._session_file, "w", encoding="utf-8"))
        except Exception:
            pass

        # Dispose all pages/views before app quits to avoid profile-release warning
        try:
            for i in range(self.browser_tabs.count()):
                w = self.browser_tabs.widget(i)
                if isinstance(w, QWebEngineView):
                    p = w.page()
                    w.setPage(None)
                    if p:
                        p.deleteLater()
                    w.deleteLater()
        except Exception:
            pass

        super().closeEvent(e)
