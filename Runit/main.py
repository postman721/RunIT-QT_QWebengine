#RunIT-QT Browser Copyright (c) 2015 JJ Posti <techtimejourney.net>" 
#RunIT-QT  comes with ABSOLUTELY NO WARRANTY;  This is free software, and you are welcome to redistribute it under  GPL Version 2, June 1991 This is the 1.0 RC1 (February 2024).

import sys
sys.dont_write_bytecode = True

import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, QTabWidget, QToolBar, QStatusBar,
                             QLabel, QLineEdit, QFileDialog, QMenu, QTabBar)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
from PyQt5.QtCore import QUrl, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from download import *
import re

class CustomTabBar(QTabBar):
    tabDoubleClicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

    def mouseDoubleClickEvent(self, event):
        index = self.tabAt(event.pos())
        if index >= 0:
            self.tabDoubleClicked.emit(index)
        else:
            super().mouseDoubleClickEvent(event)

class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super(CustomWebEnginePage, self).__init__(parent)
        self.settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)

class CustomWebEngineView(QWebEngineView):
    def __init__(self, main_window, parent=None):
        super(CustomWebEngineView, self).__init__(parent)
        self.main_window = main_window
        self.setPage(CustomWebEnginePage(self))
        # Enable full screen
        self.page().fullScreenRequested.connect(self.handleFullScreenRequested)
        # Enable JavaScript, which is crucial for modern web apps
        self.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        # Enable local storage and HTML5 local storage
        self.settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        # Enable plugins like PDF viewer which are built into Chromium
        self.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        # Enable scroll bars
        self.settings().setAttribute(QWebEngineSettings.ShowScrollBars, True)

    def handleFullScreenRequested(self, request):
        request.accept()
        if request.toggleOn():
            self.main_window.enterFullScreen()
        else:
            self.main_window.exitFullScreen()

    def contextMenuEvent(self, event):
        menu = QMenu(self)

        # Add "Open New Tab" action
        open_new_tab_action = QAction("Open New Tab", self)
        open_new_tab_action.triggered.connect(self.open_new_tab_context_menu)
        menu.addAction(open_new_tab_action)

        open_in_new_tab = QAction("Open in new tab", self)
        open_in_new_tab.triggered.connect(self.open_new_tab)
        menu.addAction(open_in_new_tab)

        close_tab_action = QAction("Close Tab", self)
        close_tab_action.triggered.connect(self.close_tab)
        menu.addAction(close_tab_action)

        download_link_action = QAction("Download", self)
        download_link_action.triggered.connect(self.download_link)
        menu.addAction(download_link_action)

        # Add bookmark action
        bookmark_action = QAction("Bookmark this page", self)
        bookmark_action.triggered.connect(lambda: self.main_window.add_bookmark_from_view(self))
        menu.addAction(bookmark_action)

        # View bookmarks action
        view_bookmarks_action = QAction("View Bookmarks", self)
        view_bookmarks_action.triggered.connect(self.main_window.open_bookmarks)
        menu.addAction(view_bookmarks_action)
        
        # Zoom In Action
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        menu.addAction(zoom_in_action)

        # Zoom Out Action
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        menu.addAction(zoom_out_action)
        
        menu.exec_(event.globalPos())

    def inspect_element(self):
        self.page().triggerAction(QWebEnginePage.InspectElement)

    def zoom_in(self):
        current_zoom = self.zoomFactor()
        self.setZoomFactor(current_zoom + 0.1)

    def zoom_out(self):
        current_zoom = self.zoomFactor()
        self.setZoomFactor(current_zoom - 0.1)

    def open_new_tab_context_menu(self):
        # Call the add_new_tab method of the main window
        self.main_window.add_new_tab()

    def open_new_tab(self):
        if self.page().contextMenuData().linkUrl().isValid():
            link_url = self.page().contextMenuData().linkUrl()
            self.main_window.add_new_tab(link_url)

    def download_link(self):
        if self.page().contextMenuData().linkUrl().isValid():
            link_url = self.page().contextMenuData().linkUrl().toString()
            self.show_download_dialog(link_url)
            
    def show_download_dialog(self, url):
        dialog = DownloadDialog(self)
        dialog.set_url(url)
        dialog.exec_()
        
    def close_tab(self):
        self.main_window.close_current_tab()

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("RunIT-QT")
        self.setGeometry(100, 100, 1200, 600)
        QIcon.setThemeName('Adwaita')

        # Load and apply the style sheet
        with open('style.qss', 'r') as f:
            style = f.read()
            self.setStyleSheet(style)
            
        # Initialize the QTabWidget
        self.browser_tabs = QTabWidget()
        self.browser_tabs.setTabBar(CustomTabBar(self.browser_tabs))
        self.browser_tabs.tabBar().tabDoubleClicked.connect(self.on_tab_double_clicked)
        self.setCentralWidget(self.browser_tabs)
        # Status bar
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Navigation bar
        self.navigation_bar = QToolBar("Navigation")
        self.addToolBar(self.navigation_bar)

        # Back button
        back_btn = QAction(QIcon.fromTheme("go-previous"), "Back", self)
        back_btn.triggered.connect(lambda: self.current_tab().back())
        self.navigation_bar.addAction(back_btn)

        # Forward button
        forward_btn = QAction(QIcon.fromTheme("go-next"), "Forward", self)
        forward_btn.triggered.connect(lambda: self.current_tab().forward())
        self.navigation_bar.addAction(forward_btn)

        # Reload button
        reload_btn = QAction(QIcon.fromTheme("view-refresh"), "Reload", self)
        reload_btn.triggered.connect(lambda: self.current_tab().reload())
        self.navigation_bar.addAction(reload_btn)

        # Home button
        home_btn = QAction(QIcon.fromTheme("go-home"), "Home", self)
        home_btn.triggered.connect(self.navigate_home)
        self.navigation_bar.addAction(home_btn)

        # Address bar
        self.address_bar = QLineEdit(self)
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        self.navigation_bar.addWidget(self.address_bar)

        # Add a new tab
        self.add_new_tab(QUrl('https://www.google.com'))
        self.show()
        
    def on_tab_double_clicked(self, index):
        self.add_new_tab()

    def add_bookmark_from_view(self, view):
        if view:
            url = view.page().url().toString()
            title = view.page().title()
            self.add_bookmark(url, title)

    def add_bookmark(self, url, title):
        # Bookmarking logic
        home = os.path.expanduser("~")
        with open(os.path.join(home, '.bookmarks.html'), 'a') as f:
            f.write(f"<br><a href='{url}'>{title}</a>")
        self.status.showMessage("Bookmarked: " + title)

    def open_bookmarks(self):
        # Logic to open bookmarks
        home = os.path.expanduser("~")
        bookmark_file = os.path.join(home, '.bookmarks.html')
        self.add_new_tab(QUrl.fromLocalFile(bookmark_file), "Bookmarks")

    def add_new_tab(self, qurl=None, label="New Tab"):
        if qurl is None:
            qurl = QUrl('about:blank')
        browser = CustomWebEngineView(self)
        browser.setUrl(qurl)
        i = self.browser_tabs.addTab(browser, label)
        self.browser_tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_urlbar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser:
                                     self.tab_title_changed(i, browser))
        # Create a tab close button
        close_button = QPushButton("X")
        close_button.clicked.connect(lambda: self.close_tab(i))
        close_button.setObjectName("closeButton")  # Set object name for styling

        # Add the close button to the tab
        self.browser_tabs.setTabText(i, label)
        self.browser_tabs.tabBar().setTabButton(i, QTabBar.RightSide, close_button)

    def current_tab(self):
        return self.browser_tabs.currentWidget()

    def navigate_home(self):
        self.current_tab().setUrl(QUrl("https://www.google.com"))
        
    def navigate_to_url(self):
        text = self.address_bar.text()
        text = text.strip()  # Remove leading/trailing whitespace
        
        # Check if the text is a URL or a search query
        if self.is_url(text):
            q = QUrl(text)
            if q.scheme() == "":
                q.setScheme("https")  # Default to HTTPS if no scheme is provided
        else:
            # Format the text as a Google search query
            search_query = '+'.join(text.split())  # Replace spaces with plus signs
            q = QUrl(f"https://www.google.com/search?q={search_query}")

        self.current_tab().setUrl(q)

    def show_warning(self, message):
        # Display the warning message in the status bar, or consider using QMessageBox for a dialog
        self.status.showMessage(message, 5000)  # Display for 5 seconds

    def is_url(self, text):
        # Check if the text follows the pattern of a URL
        pattern = r'^(https?://)?(www\.)?([\da-z\.-]+)\.([a-z\.]{2,6})([/\w \.-]*)*/?$'
        return re.match(pattern, text) is not None
        
    def update_urlbar(self, q, browser=None):
        if browser != self.current_tab():
            return
        self.address_bar.setText(q.toString())

    def tab_title_changed(self, i, browser):
        self.browser_tabs.setTabText(i, browser.page().title())
        
    def close_current_tab(self, index=None):
        if index is None:
            index = self.browser_tabs.currentIndex()
        if self.browser_tabs.count() > 1:
            web_view = self.browser_tabs.widget(index)  # Get the web view in the tab
            web_view.page().triggerAction(QWebEnginePage.Stop)  # Stop any ongoing media playback
            web_view.deleteLater()  # Optionally delete the web view to ensure resources are released
            self.browser_tabs.removeTab(index)  # Now remove the tab
      
#Close tab with x - does not apply to tab0.
    def close_tab(self, index):
        if self.browser_tabs.count() > 1:
            web_view = self.browser_tabs.widget(index)  # Get the web view in the tab
            web_view.page().triggerAction(QWebEnginePage.Stop)  # Stop any ongoing media playback
            web_view.deleteLater()  # Optionally delete the web view to ensure resources are released
            self.browser_tabs.removeTab(index)  # Now remove the tab
                     
    def enterFullScreen(self):
        self.showFullScreen()
        self.navigation_bar.hide()
        self.status.hide()
        self.browser_tabs.tabBar().setVisible(False)

    def exitFullScreen(self):
        self.showNormal()
        self.navigation_bar.show()
        self.status.show()
        self.browser_tabs.tabBar().setVisible(True)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Browser()
    sys.exit(app.exec_())
