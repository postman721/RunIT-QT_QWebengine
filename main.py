#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py — Entry point for RunIT-QT PyQt WebEngine browser.

This just wires up QApplication and the Browser window.
"""

import os
import sys

# ---------------------------------------------------------
# Disable .pyc bytecode generation for this interpreter.
# This affects imports of all other modules in this process.
# ---------------------------------------------------------
sys.dont_write_bytecode = True
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

from qt_compat import QApplication, API_NAME, PYQT_VER, QT_VER
from config import APP_NAME
from browser import Browser


def main():
    app = QApplication(sys.argv)
    w = Browser()

    banner = f"{API_NAME} {PYQT_VER} (Qt {QT_VER})"
    print(banner, flush=True)

    try:
        w.status.showMessage(banner, 5000)
        w.setWindowTitle(f"{APP_NAME} — {banner}")
    except Exception:
        pass

    sys.exit(getattr(app, "exec", getattr(app, "exec_", lambda: 0))())


if __name__ == "__main__":
    main()
