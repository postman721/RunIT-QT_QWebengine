# -*- coding: utf-8 -*-
"""
web_profile.py — QWebEngineProfile factory.

build_lean_profile() creates a minimal, memory-friendly profile:
- No disk cache (or off-the-record if supported).
- In-memory cookies only.
- Common WebEngine features turned on for compatibility.
"""

from qt_compat import (
    QApplication,
    QWebEngineProfile,
    QWebEngineSettings,
    _HTTP_CACHE,
    _COOKIES,
    _set_web_attr,
)


def build_lean_profile():
    """
    Create a QWebEngineProfile optimised for low persistence and low overhead.
    """
    app = QApplication.instance()
    try:
        # Named profile parented by the app so it's destroyed last.
        prof = QWebEngineProfile("lean-profile", app)
    except Exception:
        try:
            prof = QWebEngineProfile(app)
        except Exception:
            prof = QWebEngineProfile()

    # Try to go "off the record" (no on-disk storage).
    try:
        if hasattr(prof, "setOffTheRecord"):
            prof.setOffTheRecord(True)
        else:
            if hasattr(prof, "setCachePath"):
                prof.setCachePath("")
            if hasattr(prof, "setPersistentStoragePath"):
                prof.setPersistentStoragePath("")
            if hasattr(prof, "setPersistentCookiesPolicy"):
                prof.setPersistentCookiesPolicy(_COOKIES("NoPersistentCookies"))
    except Exception:
        pass

    # Disable HTTP cache for this profile
    try:
        prof.setHttpCacheType(_HTTP_CACHE("NoCache"))
        prof.setHttpCacheMaximumSize(0)
    except Exception:
        pass

    # Enable common features that many websites depend on
    s = prof.settings()
    for name in [
        "FullScreenSupportEnabled",
        "JavascriptEnabled",
        "LocalStorageEnabled",
        "AutoLoadImages",
        "WebGLEnabled",
        "Accelerated2dCanvasEnabled",
    ]:
        _set_web_attr(s, name, True)

    # Flash/plugins disabled by default
    _set_web_attr(s, "PluginsEnabled", False)

    # Allow mixed content for compatibility; change to False for strict HTTPS.
    _set_web_attr(s, "AllowRunningInsecureContent", True)

    return prof
