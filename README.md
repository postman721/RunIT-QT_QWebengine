# RunIT-QT_QWebengine
RunIT Browser (QWebEngine version)

 
### Features
 
    Tabbed Browsing:
        Users can open multiple web pages in separate tabs. 
        Easy navigation between different tabs.
        Open new tabs either by double clicking an existing one or via right-click menu.

    Navigation Controls:
        Back and Forward buttons to navigate through the web history.
        Refresh button to reload the current web page.
        Home button to quickly return to the home page (default set to Google).

    Bookmarking System:
        Ability to bookmark favorite web pages.
        Bookmarks are saved locally for later access.
        Option to view all bookmarked pages.
        Bookmarks are located at .bookmarks.html, which is inside user's home directory.
        
    Full screen Youtube etc.
        Full screen mode is now working on Youtube etc.        

    Context Menu:
        Right-click context menu with various options.
        Option to open links in a new tab.
        Ability to download hyperlinks and files via dedicated right-click dialog program (Download).
        Context menu has, for example: bookmarking, showing the bookmarks, dowload(the object under cursor), zoom in, zoom out and tab controls.

    Address Bar:
        Enter URLs to navigate to specific web pages.
        Input search queries that default to Google search when not a URL.
        Automatic redirection to HTTPS to enhance security.

    Download Functionality:
        Context menu option to download resources from web pages (Download).

    User Interface:
        Modern and clean user interface.
        Responsive design that adjusts to window resizing.

    Status Bar:
        Displays status messages (e.g., when a bookmark is added).

    Close Tab Option:
        Each tab comes with a close button ('X') for easy closure.
        Ability to close tabs without navigating to them.

    URL Validation:
        Basic validation to check if the entered text is a URL or a search query.
        Checks for secure HTTP (HTTPS) URLs.

    Customization and Extensibility:
        The browser can be easily customized and extended with more features.
        The style can be modified using the style.qss file.

    Error Handling:
        Basic error handling for network issues or invalid URLs.

###### <b>Notice. Download downloads whatever is under the mouse cursor when context menu is opened and the download option is chosen. Remember the choose the download location.</b>

### Running the Application

    Dependencies (Debian base as a model)
        python3-pyqt5.qtwebengine python3-pyqt5 ca-certificates wget
    
        Optional but very much recommended: adwaita-icon-theme (for icons)
    
    Running the app:
        Clone or download the source code.
        Run the the program: python3 main.py 


_______________________________________
