# -*- coding: utf-8 -*-
"""
web_page.py — Custom QWebEnginePage implementation.

SecurePage provides:
- Automatic HTTP → HTTPS upgrade for main-frame navigation.
- Certificate error handling to update the lock icon.
- Optional JS console logging (controlled via env).
- Strict feature permissions (only fullscreen is granted).
"""

from qt_compat import (
    QtCore,
    QUrl,
    QWebEnginePage,
    FEATURE,
    PERM_GRANT,
    PERM_DENY,
    _set_web_attr,
    RUNIT_JS_CONSOLE,
)


class SecurePage(QWebEnginePage):
    """
    Hardened QWebEnginePage:
    - Forces HTTPS when possible.
    - Exposes a callback to update the UI lock icon.
    - Denies most special features except fullscreen.
    """

    def __init__(self, profile, parent=None, lock_cb=None):
        super().__init__(profile, parent)
        self._lock_cb = lock_cb

        # Enable some useful settings per-page
        try:
            _set_web_attr(self.settings(), "FullScreenSupportEnabled", True)
            _set_web_attr(self.settings(), "AllowRunningInsecureContent", True)
            _set_web_attr(self.settings(), "JavascriptEnabled", True)
            _set_web_attr(self.settings(), "AutoLoadImages", True)
        except Exception:
            pass

    # ---------- Navigation policy ----------
    def acceptNavigationRequest(self, url: QUrl, nav_type, is_main_frame: bool):
        """
        Auto-upgrade http:// to https:// for main-frame navigation.
        """
        try:
            if is_main_frame and (url.scheme() or "").lower() == "http":
                secure = QUrl(url)
                secure.setScheme("https")
                self.setUrl(secure)
                return False
        except Exception:
            pass
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)

    # ---------- Certificate handling ----------
    def certificateError(self, error):
        """
        On TLS errors we mark the connection as insecure and reject the certificate.
        """
        try:
            if self._lock_cb:
                self._lock_cb(False)
        except Exception:
            pass
        return False  # do not ignore errors

    # ---------- Console logging ----------
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        """
        Optionally print JS console messages to stdout when RUNIT_JS_CONSOLE=1.
        """
        if RUNIT_JS_CONSOLE:
            print(f"js[{str(level)}] {sourceID}:{lineNumber}: {message}", flush=True)

    # ---------- Permissions ----------
    def featurePermissionRequested(self, url, feature):
        """
        Automatically grant fullscreen, deny everything else.
        """
        try:
            f_full = FEATURE("FullScreen")
            self.setFeaturePermission(
                url,
                feature,
                PERM_GRANT() if feature == f_full else PERM_DENY(),
            )
        except Exception:
            pass
