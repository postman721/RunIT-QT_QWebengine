#RunIT-QT Browser Downloader Copyright (c) 2015 JJ Posti <techtimejourney.net>" 
#RunIT-QT Browser Downloader comes with ABSOLUTELY NO WARRANTY;  This is free software, and you are welcome to redistribute it under  GPL Version 2, June 1991 This is the 1.0 RC1 (February 2024).


from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QPushButton, QProgressBar, QMessageBox, QFileDialog, QApplication, QMenu
)
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
import time
import os
import sys
sys.dont_write_bytecode = True

class DownloadDialog(QDialog):
    def __init__(self, parent=None):
        super(DownloadDialog, self).__init__(parent)
        self.setWindowTitle("Download Link")
        self.setGeometry(100, 100, 400, 200)
        self.setFixedSize(400, 200)  # Prevent resizing
        self.manager = None
        self.reply = None
        self.start_time = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # URL input field setup
        self.url_label = QLabel("Download URL:", self)
        self.url_edit = QLineEdit(self)
        self.url_edit.setReadOnly(False)
        self.url_edit.setContextMenuPolicy(Qt.CustomContextMenu)
        self.url_edit.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.url_label)
        layout.addWidget(self.url_edit)

        # Save location setup
        self.save_location_label = QLabel("Save to:", self)
        self.save_location_edit = QLineEdit(self)
        layout.addWidget(self.save_location_label)
        layout.addWidget(self.save_location_edit)

        # Browse button setup
        self.save_location_button = QPushButton("Browse", self)
        self.save_location_button.clicked.connect(self.browse_location)
        browse_layout = QHBoxLayout()
        browse_layout.addWidget(self.save_location_edit)
        browse_layout.addWidget(self.save_location_button)
        layout.addLayout(browse_layout)

        # Progress bar setup
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        # Speed and time label setup
        self.speed_time_label = QLabel(self)
        layout.addWidget(self.speed_time_label)

        # Download and cancel buttons setup
        button_layout = QHBoxLayout()
        self.download_button = QPushButton("Download", self)
        self.download_button.clicked.connect(self.download)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.cancel_download)
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

    def show_context_menu(self, position):
        menu = QMenu()
        copy_action = menu.addAction("Copy")
        paste_action = menu.addAction("Paste")
        action = menu.exec_(self.url_edit.mapToGlobal(position))
        if action == copy_action:
            self.url_edit.copy()
        elif action == paste_action:
            self.url_edit.paste()

    def set_url(self, url):
        self.url_edit.setText(url)
        suggested_filename = QUrl(url).fileName()
        if suggested_filename:
            self.save_location_edit.setText(suggested_filename)

    def browse_location(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        suggested_filename = self.save_location_edit.text()
        fileName, _ = QFileDialog.getSaveFileName(self, "Save as", suggested_filename, "All Files (*)", options=options)
        if fileName:
            self.save_location_edit.setText(fileName)

    def download(self):
        self.download_button.setDisabled(True)  # Disable the download button
        url = QUrl(self.url_edit.text())
        if not url.isValid():
            QMessageBox.warning(self, "Error", "Invalid URL")
            return

        save_location = self.save_location_edit.text()
        if not save_location:
            QMessageBox.warning(self, "Error", "No save location specified")
            return

        # Check if file already exists
        if os.path.exists(save_location):
            overwrite = QMessageBox.question(self, "Overwrite File", "File already exists. Overwrite?")
            if overwrite != QMessageBox.Yes:
                return

        self.manager = QNetworkAccessManager(self)
        self.reply = self.manager.get(QNetworkRequest(url))
        self.reply.downloadProgress.connect(self.update_progress)
        self.reply.finished.connect(self.download_finished)
        self.start_time = time.time()

    def update_progress(self, bytes_received, bytes_total):
        # Scale factor for large files
        scale_factor = 1
        if bytes_total > 2147483647:
            scale_factor = (bytes_total // 2147483647) + 1

        scaled_total = bytes_total // scale_factor
        scaled_received = bytes_received // scale_factor

        self.progress_bar.setMaximum(scaled_total)
        self.progress_bar.setValue(scaled_received)

        elapsed_time = time.time() - self.start_time
        if elapsed_time > 0:
            speed = bytes_received / elapsed_time
            remaining_time = ((bytes_total - bytes_received) / speed) if bytes_total > bytes_received else 0
            self.speed_time_label.setText(f"Speed: {speed/1024:.2f} KB/s, Time left: {remaining_time:.2f} seconds")
            
    def download_finished(self):
        if self.reply.error() == QNetworkReply.NoError and self.reply.isFinished():
            file_data = self.reply.readAll()
            with open(self.save_location_edit.text(), 'wb') as file:
                file.write(file_data)
            QMessageBox.information(self, "Download Complete", "The download was completed successfully.")
            self.accept()
            self.download_button.setDisabled(False)  # Enable the download button
        else:
            self.download_error(self.reply.error())

    def download_error(self, error):
        QMessageBox.warning(self, "Download Stopped", "An error occurred during the download.")
        self.download_button.setDisabled(False)

    def cancel_download(self):
        if self.reply is not None:
            self.reply.abort()
        self.download_button.setDisabled(False)  # Re-enable the download button
        # Optionally, reset other UI elements to their initial state here
        self.progress_bar.setValue(0)
        self.speed_time_label.setText("")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Styling
    style = '''
    QMainWindow {
        background-color: #f0f0f0;
    }
    QToolBar {
        background-color: #e0e0e0;
        border: none;
    }
    QLineEdit {
        background-color: #ffffff;
        border: 1px solid #cccccc;
    }
    QPushButton, QLabel, QTabBar::tab {
        background-color: #d0d0d0;
        color: #000000;
    }
    QPushButton:hover, QTabBar::tab:hover {
        background-color: #b0b0b0;
    }
    QPushButton:pressed, QTabBar::tab:selected {
        background-color: #a0a0a0;
    }
    QTabWidget::pane {
        border: none;
    }
    #closeButton {
        background-color: transparent;
        border: none;
        width: 16px;
        height: 16px;
    }
    '''

    # Apply the stylesheet
    app.setStyleSheet(style)

    dialog = DownloadDialog()
    dialog.exec_()
