# RunIT-QT Browser Downloader (enhanced) — PyQt5/6 compatible, memory-lean
# Default download directory: ~/Downloads
# Automatic filename sanitization and extension appending from MIME type.
#
# Copyright (c) 2015 JJ Posti
# GPL v2 (June 1991).

import os
import sys
import time
import re

# -------- Qt compat imports --------
try:
    from PyQt6 import QtCore, QtWidgets, QtNetwork
    QT6 = True
except ImportError:
    from PyQt5 import QtCore, QtWidgets, QtNetwork
    QT6 = False

QUrl = QtCore.QUrl
Qt = QtCore.Qt
QDialog = QtWidgets.QDialog
QVBoxLayout = QtWidgets.QVBoxLayout
QLabel = QtWidgets.QLabel
QLineEdit = QtWidgets.QLineEdit
QHBoxLayout = QtWidgets.QHBoxLayout
QPushButton = QtWidgets.QPushButton
QProgressBar = QtWidgets.QProgressBar
QMessageBox = QtWidgets.QMessageBox
QFileDialog = QtWidgets.QFileDialog
QApplication = QtWidgets.QApplication

QNetworkAccessManager = QtNetwork.QNetworkAccessManager
QNetworkRequest = QtNetwork.QNetworkRequest
QNetworkReply = QtNetwork.QNetworkReply


def MSGBOX_YES():
    # QMessageBox.Yes (Qt5) => QMessageBox.StandardButton.Yes (Qt6)
    return getattr(
        QMessageBox,
        "Yes",
        getattr(QMessageBox.StandardButton, "Yes"),
    )


def REDIRECT_ATTR():
    # Qt5: QNetworkRequest.RedirectionTargetAttribute
    # Qt6: QNetworkRequest.Attribute.RedirectionTargetAttribute
    return getattr(
        QNetworkRequest,
        "RedirectionTargetAttribute",
        getattr(QNetworkRequest.Attribute, "RedirectionTargetAttribute"),
    )


def CONTENT_LENGTH_HEADER():
    # Qt5: QNetworkRequest.ContentLengthHeader
    # Qt6: QNetworkRequest.KnownHeaders.ContentLengthHeader
    return getattr(
        QNetworkRequest,
        "ContentLengthHeader",
        getattr(QNetworkRequest.KnownHeaders, "ContentLengthHeader", None),
    )


def CONTENT_TYPE_HEADER():
    # Qt5: QNetworkRequest.ContentTypeHeader
    # Qt6: QNetworkRequest.KnownHeaders.ContentTypeHeader
    return getattr(
        QNetworkRequest,
        "ContentTypeHeader",
        getattr(QNetworkRequest.KnownHeaders, "ContentTypeHeader", None),
    )


def APP_EXEC(app):
    return app.exec() if hasattr(app, "exec") else app.exec_()


sys.dont_write_bytecode = True

# -------- MIME → extension map --------

MIME_EXT = {
    "application/pdf": ".pdf",
    "application/zip": ".zip",
    "application/x-zip-compressed": ".zip",
    "application/x-rar-compressed": ".rar",
    "application/x-7z-compressed": ".7z",
    "application/x-msdownload": ".exe",
    "application/vnd.debian.binary-package": ".deb",
    "application/x-rpm": ".rpm",
    "application/octet-stream": ".bin",

    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "image/bmp": ".bmp",

    "video/mp4": ".mp4",
    "video/webm": ".webm",
    "video/x-msvideo": ".avi",
    "video/x-matroska": ".mkv",

    "audio/mpeg": ".mp3",
    "audio/ogg": ".ogg",
    "audio/wav": ".wav",
    "audio/flac": ".flac",

    "text/plain": ".txt",
    "text/html": ".html",
    "text/css": ".css",
    "text/javascript": ".js",
}


# -------- helpers: Downloads dir + filename sanitization --------

def default_download_dir() -> str:
    """
    Return the platform-appropriate default download directory.

    For this browser we always use ~/Downloads by design.
    """
    home = os.path.expanduser("~")
    downloads = os.path.join(home, "Downloads")
    try:
        os.makedirs(downloads, exist_ok=True)
    except Exception:
        # If creation fails, fall back to home
        return home
    return downloads


_RESERVED_WIN_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def _sanitize_filename(name: str, default: str = "download") -> str:
    """
    Make 'name' safe to use as a filename on most filesystems.

    - Strips path components.
    - Replaces unsafe characters with '_'.
    - Avoids leading dot (no accidental hidden files).
    - Avoids empty name and Windows reserved basenames.
    """
    name = name or ""
    # 1) Drop any path component if present (just in case)
    name = os.path.basename(name.strip())

    # 2) Replace unsafe characters (keep letters, digits, dot, dash, underscore)
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)

    # 3) Avoid leading dot (hidden files on Unix)
    name = name.lstrip(".")
    if not name:
        name = default

    # 4) Avoid silly length
    if len(name) > 255:
        base, ext = os.path.splitext(name)
        name = base[:200] + ext

    # 5) Avoid Windows reserved names (basename only)
    base, ext = os.path.splitext(name)
    if base.upper() in _RESERVED_WIN_NAMES:
        base = f"{base}_file"
        name = base + ext

    return name or default


def _append_extension_if_missing(filename: str, mime: str) -> str:
    """
    If the filename has no extension, append one based on MIME type.

    Only modifies filenames that have *no* extension.
    """
    base, ext = os.path.splitext(filename)
    if ext:  # already has extension
        return filename

    if not mime:
        return filename

    mime = mime.lower().split(";", 1)[0].strip()
    ext_guess = MIME_EXT.get(mime)
    if not ext_guess:
        return filename

    return base + ext_guess


class DownloadDialog(QDialog):
    def __init__(self, parent=None, preset_url: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Download")
        self.setFixedSize(480, 260)

        self.manager = None
        self.reply = None
        self.file = None
        self.tmp_path = None
        self.final_path = None
        self.start_time = None
        self.redirects = 0
        self.max_redirects = 5
        self.user_agent = (
            b"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/538.1 "
            b"(KHTML, like Gecko) RunIT-QT Downloader Safari/538.1"
        )

        # Memory/IO controls
        self.CHUNK = 64 * 1024         # 64 KiB read/write chunks
        self.READBUF = 256 * 1024      # 256 KiB Qt internal buffer cap
        self._last_ui_update = 0.0     # throttle progress updates
        self._ui_interval = 0.10       # seconds
        self._bytes_received = 0       # local counter (robust even if progress signal skipped)
        self._total_bytes = -1         # from Content-Length, if known
        self._preallocated = False

        # MIME type from headers (used to append extension)
        self._mime = ""

        self._build_ui()
        if preset_url:
            self.set_url(preset_url)

    # ---------- UI ----------
    def _build_ui(self):
        lay = QVBoxLayout(self)

        self.url_label = QLabel("Download URL:", self)
        self.url_edit = QLineEdit(self)
        lay.addWidget(self.url_label)
        lay.addWidget(self.url_edit)

        self.path_label = QLabel("Save to:", self)
        self.path_edit = QLineEdit(self)
        btn_browse = QPushButton("Browse…", self)
        row = QHBoxLayout()
        row.addWidget(self.path_edit)
        row.addWidget(btn_browse)
        lay.addWidget(self.path_label)
        lay.addLayout(row)

        self.progress = QProgressBar(self)
        self.progress.setTextVisible(True)
        lay.addWidget(self.progress)

        self.speed = QLabel("", self)
        lay.addWidget(self.speed)

        row2 = QHBoxLayout()
        self.btn_go = QPushButton("Download", self)
        self.btn_cancel = QPushButton("Cancel", self)
        row2.addWidget(self.btn_go)
        row2.addWidget(self.btn_cancel)
        lay.addLayout(row2)

        btn_browse.clicked.connect(self._browse)
        self.btn_go.clicked.connect(self.start_download)
        self.btn_cancel.clicked.connect(self._cancel)

    # ---------- Public helpers ----------
    def set_url(self, url: str):
        """
        Set the URL field and auto-fill a sane default path:
        ~/Downloads/<sanitized-filename>
        """
        self.url_edit.setText(url)

        # Derive filename from URL, then sanitize it
        raw_name = QUrl(url).fileName() or "download"
        safe_name = _sanitize_filename(raw_name)

        downloads = default_download_dir()

        # Only auto-fill if user hasn't typed anything manually
        if not self.path_edit.text().strip():
            self.path_edit.setText(os.path.join(downloads, safe_name))

    @staticmethod
    def download_url(parent=None, url: str = ""):
        """Convenience launcher usable from anywhere in the app."""
        dlg = DownloadDialog(parent, preset_url=url or "")
        (dlg.exec() if hasattr(dlg, "exec") else dlg.exec_())
        return dlg

    # ---------- Internals ----------
    def _browse(self):
        """
        Open a native "Save As" dialog, starting in ~/Downloads
        and always suggesting a sanitized filename.
        """
        downloads = default_download_dir()

        # Current text or derived from URL, then sanitized
        current = self.path_edit.text().strip()
        if current:
            # User may have typed a path; sanitize only the basename
            dirpath, base = os.path.split(current)
            dirpath = dirpath or downloads
            safe_base = _sanitize_filename(base or "download")
            start_path = os.path.join(dirpath, safe_base)
        else:
            raw_name = QUrl(self.url_edit.text()).fileName() or "download"
            safe_name = _sanitize_filename(raw_name)
            start_path = os.path.join(downloads, safe_name)

        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save as",
            start_path,
            "All files (*)",
        )
        if path:
            # Sanitize only the filename part, keep the directory as user chose
            dirpath, base = os.path.split(path)
            safe_base = _sanitize_filename(base or "download")
            self.path_edit.setText(os.path.join(dirpath or downloads, safe_base))

    def start_download(self):
        self.btn_go.setDisabled(True)

        url = QUrl(self.url_edit.text().strip())
        if not url.isValid() or (hasattr(url, "isEmpty") and url.isEmpty()):
            QMessageBox.warning(self, "Download", "Invalid URL.")
            self.btn_go.setDisabled(False)
            return

        path = self.path_edit.text().strip()
        if not path:
            QMessageBox.warning(self, "Download", "Choose a save location.")
            self.btn_go.setDisabled(False)
            return

        # Sanitize final filename, keep dir as-is
        dirpath, base = os.path.split(path)
        dirpath = dirpath or default_download_dir()
        safe_base = _sanitize_filename(base or "download")

        # We don't yet know MIME here, so we *don't* append extension yet.
        # That will happen later in _on_finished() once headers are known.
        path = os.path.join(dirpath, safe_base)

        if os.path.isdir(path):
            QMessageBox.warning(self, "Download", "Save path points to a directory.")
            self.btn_go.setDisabled(False)
            return

        if os.path.exists(path):
            r = QMessageBox.question(self, "Overwrite", "File exists. Overwrite?")
            if r != MSGBOX_YES():
                self.btn_go.setDisabled(False)
                return

        # temp file path for atomic replace
        self.final_path = path
        self.tmp_path = path + ".part"

        try:
            # open in binary, unbuffered small buffer to reduce Python-side RAM
            self.file = open(self.tmp_path, "wb", buffering=0)
        except Exception as e:
            QMessageBox.critical(self, "Download", f"Cannot open file:\n{e}")
            self.btn_go.setDisabled(False)
            return

        self._kickoff_request(url)

    def _kickoff_request(self, url: QUrl):
        if self.manager is None:
            self.manager = QNetworkAccessManager(self)

        req = QNetworkRequest(url)
        req.setRawHeader(b"User-Agent", self.user_agent)

        self.reply = self.manager.get(req)

        # Limit the internal read buffer to keep RAM bounded
        try:
            self.reply.setReadBufferSize(self.READBUF)
        except Exception:
            pass

        # Signals
        self.reply.readyRead.connect(self._on_ready_read)
        self.reply.downloadProgress.connect(self._on_progress)
        self.reply.finished.connect(self._on_finished)
        if hasattr(self.reply, "metaDataChanged"):
            self.reply.metaDataChanged.connect(self._on_headers)
        if hasattr(self.reply, "errorOccurred"):
            self.reply.errorOccurred.connect(self._on_error)
        else:
            self.reply.error.connect(self._on_error)

        self.start_time = time.time()
        self._last_ui_update = 0.0
        self._bytes_received = 0
        self._total_bytes = -1
        self._preallocated = False
        self._mime = ""

        self.progress.setValue(0)
        self.progress.setMaximum(0)  # unknown until we see bytes_total
        self.speed.setText("Starting…")

    # Grab headers early for Content-Length and MIME type, then preallocate
    def _on_headers(self):
        # Content-Length
        try:
            hdr = CONTENT_LENGTH_HEADER()
            if hdr is not None:
                v = self.reply.header(hdr)
                if v is not None:
                    try:
                        total = int(v)
                        self._total_bytes = total
                        self.progress.setMaximum(total)
                        self._maybe_preallocate(total)
                    except Exception:
                        pass
        except Exception:
            pass

        # Content-Type → MIME string
        try:
            hct = CONTENT_TYPE_HEADER()
            if hct is not None:
                v = self.reply.header(hct)
            else:
                v = None
            if v is not None:
                self._mime = str(v)
        except Exception:
            pass

    def _maybe_preallocate(self, total: int):
        if self._preallocated or total <= 0 or not self.file:
            return
        try:
            fd = self.file.fileno()
            # Best: posix_fallocate (no sparse, ensures disk reservation)
            try:
                if hasattr(os, "posix_fallocate"):
                    os.posix_fallocate(fd, 0, total)  # type: ignore
                else:
                    # Fallback: ftruncate creates a sparse file on many FS (still OK)
                    os.ftruncate(fd, total)
                # Reset position for writing
                os.lseek(fd, 0, os.SEEK_SET)
                self._preallocated = True
            except Exception:
                # Don’t fail the download; just skip preallocation
                pass
        except Exception:
            pass

    def _on_ready_read(self):
        # Read in fixed chunks to keep memory flat
        if not (self.reply and self.file):
            return
        try:
            while True:
                # limit each read to CHUNK to avoid large intermediate buffers
                data = self.reply.read(self.CHUNK)
                if not data:
                    break
                # data is 'bytes' already; write directly
                written = self.file.write(data)
                if written is None:
                    # Some platforms return None; ignore
                    pass
                self._bytes_received += len(data)
        except Exception as e:
            self._fail(f"I/O write error:\n{e}")

    def _on_progress(self, received: int, total: int):
        # Update maximum once when known
        if total > 0 and (self._total_bytes != total):
            self._total_bytes = total
            self.progress.setMaximum(total)
            self._maybe_preallocate(total)

        # Throttle UI updates to ~10 Hz
        now = time.time()
        if (now - self._last_ui_update) < self._ui_interval:
            return
        self._last_ui_update = now

        # Prefer signal values, but keep local counter as fallback
        rec = received if received >= 0 else self._bytes_received
        self.progress.setValue(int(rec))

        elapsed = max(0.001, now - self.start_time)
        speed_bps = rec / elapsed
        eta = (total - rec) / speed_bps if total > 0 and speed_bps > 0 else 0
        self.speed.setText(f"Speed: {speed_bps/1024:.1f} KB/s   ETA: {eta:.1f} s")

    def _on_finished(self):
        # Follow redirects?
        try:
            redir_attr = REDIRECT_ATTR()
            attr = self.reply.attribute(redir_attr)
        except Exception:
            attr = None

        if attr:
            self.redirects += 1
            if self.redirects > self.max_redirects:
                self._fail("Too many redirects.")
                return
            target = attr if isinstance(attr, QUrl) else QUrl(str(attr))
            if target.isRelative():
                target = self.reply.url().resolved(target)
            self.reply.deleteLater()
            self._kickoff_request(target)
            return

        # No error?
        noerr_enum = getattr(
            QNetworkReply.NetworkError,
            "NoError",
            getattr(QNetworkReply, "NoError", 0),
        )
        current_err = self.reply.error() if hasattr(self.reply, "error") else noerr_enum
        if current_err == noerr_enum:
            try:
                # Flush any pending bytes
                self._on_ready_read()
                if self.file:
                    self.file.flush()
                    os.fsync(self.file.fileno())
                    self.file.close()
                    self.file = None

                # Decide final filename (append extension if missing using MIME)
                dirpath, base = os.path.split(self.final_path)
                dirpath = dirpath or default_download_dir()
                safe_base = _sanitize_filename(base or "download")
                safe_base = _append_extension_if_missing(safe_base, self._mime)
                final_path = os.path.join(dirpath, safe_base)

                # Atomic replace: tmp_path -> final_path
                try:
                    os.replace(self.tmp_path, final_path)
                except Exception:
                    # Best-effort rename fallback
                    try:
                        if os.path.exists(final_path):
                            os.remove(final_path)
                        os.rename(self.tmp_path, final_path)
                    except Exception:
                        raise

                self.final_path = final_path

            except Exception as e:
                self._fail(f"I/O finalize error:\n{e}")
                return

            if self._total_bytes > 0:
                self.progress.setValue(self._total_bytes)
            self.speed.setText("Done.")
            QMessageBox.information(
                self,
                "Download",
                f"Download completed successfully.\n\nSaved as:\n{self.final_path}",
            )
            self.accept()
        else:
            self._cleanup()

        self.btn_go.setDisabled(False)

    def _on_error(self, code):
        msg = str(code)
        # Show basic SSL error hint if any
        try:
            if hasattr(self.reply, "sslErrors") and self.reply.sslErrors():
                msg += "\nSSL errors occurred."
        except Exception:
            pass
        self._fail(f"Network error: {msg}")

    def _cancel(self):
        if self.reply:
            try:
                self.reply.abort()
            except Exception:
                pass
        self._cleanup()
        self.reject()

    def _fail(self, message: str):
        self._cleanup()
        QMessageBox.warning(self, "Download", message)
        self.btn_go.setDisabled(False)

    def _cleanup(self):
        try:
            if self.reply:
                self.reply.deleteLater()
                self.reply = None
            if self.file:
                try:
                    self.file.close()
                except Exception:
                    pass
                self.file = None
            # Remove temp file on failure/cancel
            if self.tmp_path and os.path.exists(self.tmp_path):
                try:
                    os.remove(self.tmp_path)
                except Exception:
                    pass
        except Exception:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    d = DownloadDialog()
    d.show()
    sys.exit(APP_EXEC(app))
