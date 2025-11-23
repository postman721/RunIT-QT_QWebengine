# -*- coding: utf-8 -*-
"""
qt_compat.py — PyQt5/PyQt6 compatibility layer and common helpers.

This module:
- Detects PyQt6 vs PyQt5 at runtime.
- Exposes unified names for Qt classes used across the project.
- Provides small helper functions for WebEngine attributes and enums.
- Defines logging utilities and API/Qt version info.
"""

import os
import sys

from datetime import datetime, timedelta
try:
    # Python 3.11+
    from datetime import UTC
except Exception:
    # Python <= 3.10
    from datetime import timezone as _tz
    UTC = _tz.utc

# -------- Qt compat imports --------
try:
    from PyQt6 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets, QtNetwork
    QT6 = True
except Exception:  # Fallback to PyQt5
    from PyQt5 import QtCore, QtGui, QtWidgets, QtWebEngineWidgets, QtNetwork
    QT6 = False

Qt = QtCore.Qt
QUrl = QtCore.QUrl
QSize = QtCore.QSize

QKeySequence = QtGui.QKeySequence
QAction = QtGui.QAction if QT6 else QtWidgets.QAction
QApplication = QtWidgets.QApplication
QMainWindow = QtWidgets.QMainWindow
QToolBar = QtWidgets.QToolBar
QToolButton = QtWidgets.QToolButton
QLineEdit = QtWidgets.QLineEdit
QFileDialog = QtWidgets.QFileDialog
QTabWidget = QtWidgets.QTabWidget
QStatusBar = QtWidgets.QStatusBar
QSizePolicy = QtWidgets.QSizePolicy
QMessageBox = QtWidgets.QMessageBox

# --- WebEngine imports ---
if QT6:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import (
        QWebEngineProfile, QWebEnginePage, QWebEngineSettings,
        QWebEngineDownloadRequest as QWebEngineDownloadItem,
        QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo,
    )
else:
    from PyQt5.QtWebEngineWidgets import (
        QWebEngineView, QWebEngineProfile, QWebEngineSettings,
        QWebEnginePage, QWebEngineDownloadItem,
    )
    from PyQt5.QtWebEngineCore import (
        QWebEngineUrlRequestInterceptor, QWebEngineUrlRequestInfo,
    )

# -------- Version banner --------
API_NAME = "PyQt6" if QT6 else "PyQt5"
PYQT_VER = getattr(QtCore, "PYQT_VERSION_STR", "unknown")
QT_VER = QtCore.qVersion()

# -------- Verbose toggles --------
VERBOSE = os.environ.get("RUNIT_VERBOSE", "1") != "0"
RUNIT_JS_CONSOLE = os.environ.get("RUNIT_JS_CONSOLE", "0") == "1"


def vlog(*args):
    """
    Print debug logging if VERBOSE is enabled via environment.

    Set RUNIT_VERBOSE=0 to silence these messages.
    """
    if VERBOSE:
        print(*args, flush=True)


# ------------------ small helpers ------------------
def CURSOR(name: str):
    """Return a cursor enum value that works across Qt5/Qt6."""
    enum = getattr(Qt, "CursorShape", None)
    return getattr(enum, name) if enum else getattr(Qt, name)


def _HTTP_CACHE(name: str):
    """Compatibility wrapper for QWebEngineProfile.HttpCacheType enums."""
    enum = getattr(QWebEngineProfile, "HttpCacheType", None)
    return getattr(enum, name) if enum else getattr(QWebEngineProfile, name)


def _COOKIES(name: str):
    """Compatibility wrapper for QWebEngineProfile.PersistentCookiesPolicy."""
    enum = getattr(QWebEngineProfile, "PersistentCookiesPolicy", None)
    return getattr(enum, name) if enum else getattr(QWebEngineProfile, name)


def _set_web_attr(settings_obj, name: str, value: bool):
    """
    Safely set WebEngine settings with both Qt5 and Qt6 APIs.

    Some attributes moved under QWebEngineSettings.WebAttribute in Qt6.
    """
    enum = getattr(QWebEngineSettings, "WebAttribute", None)
    if enum is not None and hasattr(enum, name):
        settings_obj.setAttribute(getattr(enum, name), value)
    elif hasattr(QWebEngineSettings, name):
        settings_obj.setAttribute(getattr(QWebEngineSettings, name), value)


def PERM_GRANT():
    """Return the enum value for 'permission granted by user'."""
    pol = getattr(QWebEnginePage, "PermissionPolicy", None)
    return getattr(pol, "Grant") if pol else getattr(QWebEnginePage, "PermissionGrantedByUser")


def PERM_DENY():
    """Return the enum value for 'permission denied by user'."""
    pol = getattr(QWebEnginePage, "PermissionPolicy", None)
    return getattr(pol, "Deny") if pol else getattr(QWebEnginePage, "PermissionDeniedByUser")


def FEATURE(name: str):
    """Compatibility wrapper for QWebEnginePage.Feature enums."""
    e = getattr(QWebEnginePage, "Feature", None)
    return getattr(e, name) if e else getattr(QWebEnginePage, name)
