# importing required libraries
from PyQt5 import QtCore, QtGui, QtWidgets 
from PyQt5.QtCore import * 
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtWebEngineWidgets import * 
from PyQt5.QtPrintSupport import * 
import os, sys, subprocess
from subprocess import Popen  
try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s
try:
    _encoding = QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QApplication.translate(context, text, disambig)

class TabWidget(QMainWindow):
    def __init__(self, *args, **kwargs):
        QMainWindow.__init__(self, *args, **kwargs)

#Window settings.
        self.resize(1200, 800)        
        self.setWindowTitle("RunIT-QT Browser")
        self.setStyleSheet("*{color:#ffffff; padding:2px; margin:2px; background-color:#4d4a4a; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "*:selected{background-color:#4d4a4a; color:yellow}"
        "*:hover{background-color:#4d4a4a;}")
#Tabwidget creation.      
        self.tabs=QTabWidget()
        self.new_tabs(QUrl(''), 'First tab')        
        self.tabs.setDocumentMode(True)
                                   
#Navigation bar.       
        self.urlbar = QLineEdit()
        self.urlbar.setStyleSheet("QLineEdit{color:#ffffff; padding:2px; margin:2px; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QLineEdit:hover{background-color:#4d4a4a;}") 
        self.urlbar.setObjectName(_fromUtf8("lineEdit"))
        self.urlbar.setPlaceholderText("Type an address")
        self.urlbar.returnPressed.connect(self.navigation)
        
        self.urlbar.returnPressed.connect(self.navigation)
        self.urlbar.returnPressed.connect(self.navigation)

#General tab settings.
        self.setCentralWidget(self.tabs) 
        self.status = QStatusBar()
        self.setStatusBar(self.status) 
        self.navtb = QToolBar("Navigation")
        self.tabs.currentWidget().loadFinished.connect(self.title)
        self.tabs.currentWidget().urlChanged.connect(self.url_update)
        self.status.showMessage("Last Action: Opened first tab at index 0. You can start browsing now.") 
                   
#Back button before navbar adding.        
        self.back = QToolButton()
        self.back.setStyleSheet("QToolButton{color:#ffffff; padding:2px; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}")
        self.back.setText('<-')
        self.back.clicked.connect(self.backs)
        self.navtb.addWidget(self.back)
        
#Navbar comes in.         
        self.addToolBar(self.navtb)
        self.navtb.addWidget(self.urlbar)  
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.tabBarDoubleClicked.connect(self.new_tabs)
                 
#First page.
        self.url ="https://www.startpage.com/"
        self.tabs.currentWidget().load(QUrl(self.url)) 
        self.urlbar.setText(str(self.url))
        currentIndex=self.tabs.currentIndex()
        currentWidget=self.tabs.currentWidget()
        print(currentIndex)
        self.tabs.setTabText(currentIndex, str(currentIndex))
                        
############################
#Rest of the content begins
############################
#Forward.        
        self.forward = QToolButton()
        self.forward.setStyleSheet("QToolButton{color:#ffffff; padding:2px; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        self.forward.setText('->')
        self.forward.clicked.connect(self.forwards)
        self.navtb.addWidget(self.forward)

#Reload.        
        self.reloading = QToolButton()
        self.reloading.setStyleSheet("QToolButton{color:#ffffff; padding:2px; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        self.reloading.setText("Reload")
        self.reloading.setToolTip('Reload Page')
        self.reloading.clicked.connect(self.reloads)
        self.navtb.addWidget(self.reloading)
#Home.        
        self.home = QToolButton()
        self.home.setStyleSheet("QToolButton{color:#ffffff; padding:2px; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        self.home.setText('Home')
        self.home.setToolTip('Go Home')
        self.home.clicked.connect(self.homes)
        self.navtb.addWidget(self.home)
#Zoom -.        
        self.zoom_out = QToolButton()
        self.zoom_out.setStyleSheet("QToolButton{color:#ffffff; padding:2px; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        self.zoom_out.setToolTip('Zoom -')
        self.zoom_out.clicked.connect(self.zoomouts)
        self.zoom_out.setText('Zoom -')      
        self.zoom_out.setToolTip('Zoom -')
        self.navtb.addWidget(self.zoom_out)               
#Zoom +.       
        self.zoom_in = QToolButton()
        self.zoom_in.setStyleSheet("QToolButton{color:#ffffff; padding:2px; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}")
        self.zoom_in.setText('Zoom +')
        self.zoom_in.setToolTip('Zoom +')
        self.zoom_in.clicked.connect(self.zoomins)
        self.navtb.addWidget(self.zoom_in)
#Printing.        
        self.printing = QToolButton()
        self.printing.setStyleSheet("QToolButton{color:#ffffff; background-color:#353535; padding:2px; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        self.printing.setText('Print')
        self.printing.setToolTip('Print')
        self.printing.clicked.connect(self.handlePreview)
        self.navtb.addWidget(self.printing)  
#Search Switch.        
        self.switch_2 = QLineEdit()
        self.switch_2.setStyleSheet("QLineEdit{color:#ffffff; background-color:#353535; padding:2px; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QLineEdit:hover{background-color:#5c5c5c;}") 
        self.switch_2.setObjectName(_fromUtf8("switch_2"))
        self.switch_2.setPlaceholderText("Switch")
        self.switch_2.setToolTip('gs=Startpage, wiki = Wikipedia,  tube = Youtube,  eco = Ecosia. Empty = Startpage search (default)')
        self.switch_2.returnPressed.connect(self.extra)
        self.switch_2.setFixedSize(62,24)

        self.navtb.addWidget(self.switch_2)
#Search.        
        self.Search = QLineEdit()
        self.Search.setStyleSheet("QLineEdit{color:#ffffff; padding:2px; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QLineEdit:hover{background-color:#5c5c5c;}") 
        self.Search.setObjectName(_fromUtf8("Search"))
        self.Search.setPlaceholderText("Search something")
        self.Search.setToolTip('Search')
        self.Search.setFixedSize(192,24)
        self.Search.returnPressed.connect(self.extra)
        self.navtb.addWidget(self.Search)
#Bookmark.        
        self.bookmark = QToolButton()
        self.bookmark.setStyleSheet("QToolButton{color:#ffffff; padding:2px; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}")
        self.bookmark.setToolTip('Bookmark addressbar location')
        self.bookmark.setText('Bookmark')
        self.bookmark.clicked.connect(self.bookmarks)
        self.navtb.addWidget(self.bookmark)
#Open Bookmarks.        
        self.see_bookmark = QToolButton()
        self.see_bookmark.setStyleSheet("QToolButton{color:#ffffff; padding:2px; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        self.see_bookmark.setText('See Bookmarks')
        self.see_bookmark.setToolTip('See Bookmarks')
        self.see_bookmark.clicked.connect(self.bookopen)
        self.navtb.addWidget(self.see_bookmark)
#About.        
        self.about1 = QToolButton()
        self.about1.setStyleSheet("QToolButton{color:#ffffff; padding:2px; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        self.about1.setText("i")        
        self.about1.setToolTip('About')
        self.about1.clicked.connect(self.about)
        self.navtb.addWidget(self.about1)    
#Browser settings.
        self.tabs.currentWidget().page().settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.tabs.currentWidget().page().settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.tabs.currentWidget().page().settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.tabs.currentWidget().page().settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        self.tabs.currentWidget().page().settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.tabs.currentWidget().page().settings().setAttribute(QWebEngineSettings.SpatialNavigationEnabled, True)
        self.tabs.currentWidget().page().settings().setAttribute(QWebEngineSettings.AutoLoadImages, True)
        self.tabs.currentWidget().page().settings().setAttribute(QWebEngineSettings.FullScreenSupportEnabled, True)
        self.tabs.currentWidget().page().fullScreenRequested.connect(lambda request, browser=self.tabs: self.fullscreen_requested(request, browser))

###################
####Functions begin.
#####################
    def fullscreen_requested(self, request, browser):
        request.accept()

        if request.toggleOn():
            self.tabs.showFullScreen()
            self.showFullScreen()
            self.navtb.hide()
            self.status.hide()
        else:
            self.showNormal()
            self.navtb.show()
            self.status.show()

    def title(self):
        currentIndex=self.tabs.currentIndex()
        print("Title is at index " + str(currentIndex))	        	
        self.tabs.setCurrentIndex(currentIndex)
        
    def url_update(self):
        qurl = self.tabs.currentWidget().url().toString()
        self.urlbar.setText(str(qurl))       
	
#Remove tabs unless only 1 available.
    def close_tab(self, number_of_tabs):   
        if self.tabs.count() < 2 and self.tabs.currentIndex() == 0:
            print("Not removing index 0.")
            self.status.showMessage(str("Not removing index 0."))            			  
            return
        else:      
            self.tabs.removeTab(number_of_tabs) 
            
#General tab attribute funcitons.
    def navigation(self):              
        q=QUrl(self.urlbar.text())
        a="https://"
        b=""
        title = self.tabs.currentWidget().page().title()
        if q.scheme() == "":
        #Automatically use https.
            q.setScheme(a)           
            qx=str(self.urlbar.text())
            aq=a+qx
            print(aq)	
            self.urlbar.setText(aq)
            self.tabs.currentWidget().load(QUrl(aq))
            qurl = self.tabs.currentWidget().url()
            self.tabs.currentWidget()
            currentIndex=self.tabs.currentIndex()
            currentWidget=self.tabs.currentWidget()
            self.status.showMessage(str("Last loaded: " + aq + "   On tab: " + str(currentIndex)))
        elif q.scheme() == "https":
        #Automatically use https -> remove extra https here.
            q.setScheme(b)           
            qx=str(self.urlbar.text())
            bq=b+qx
            print(bq)	
            self.urlbar.setText(bq)
            self.tabs.currentWidget().load(QUrl(bq))
            qurl = self.tabs.currentWidget().url()
            self.tabs.currentWidget()
            currentIndex=self.tabs.currentIndex()
            self.tabs.currentWidget()
            self.status.showMessage(str("Last loaded: " + bq + "   On tab: " + str(currentIndex)))    
           
############################################
#When double-clicking tab open a new empty tab with these methods.
    def new_tabs(self, qurl = None, label ="Blank"):   
        browser = HtmlView()   
        ix = self.tabs.addTab(browser, "Tab")
        self.tabs.setCurrentIndex(ix)
        currentIndex=self.tabs.currentIndex()
        currentWidget=self.tabs.currentWidget()
        print(currentIndex)
        self.tabs.setTabText(currentIndex, str(currentIndex))

        browser.urlChanged.connect(lambda qurl, browser = browser:
                                   self.url_update(qurl, browser))
                                   
        browser.loadFinished.connect(lambda _, ix = ix, browser = browser:
                                     self.tabs.setTabText(ix, browser.page().title()))
 
    def url_update(self, q, browser = None):
 
        if browser != self.tabs.currentWidget():
 
            return
 
        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)
        self.title()
                                            
    def tab_open_doubleclick(self, i):        
        if i == -1: 
            self.new_tabs()  
         
    def tab_open_doubleclick(self, i):        
        if i == -1: 
            self.new_tabs()  
                            
#####Bookmark functions.    
    def bookmarks(self,widget):
        home=os.getenv("HOME")
        print (home)
        site=str(self.urlbar.text())
        os.chdir(home) 
        f = open('.bookmarks.html', 'a')
        f.write("<br>" + "<a href=" + site + ">"+ site + "</a>")
        f.close()
        currentIndex=self.tabs.currentIndex()
        self.status.showMessage(str("Last Action: Bookmarked on tab: " + str(currentIndex)))                
        
#Open bookmarks file.
    def bookopen(self,widget):
        home=os.getenv("HOME")
        print(home)
        home=os.getenv("HOME")
        os.chdir(home)
        head="file:///"
        books=".bookmarks.html"
        location=(head + home + '/' + books)
        self.tabs.currentWidget().load(QUrl(location))
        currentIndex=self.tabs.currentIndex()
        self.status.showMessage(str("Last Action: Bookmarks opened on tab: " + str(currentIndex))) 

#Home page function.
    def homes(self):
        self.home = "https://www.startpage.com/"
        self.urlbar.setText(self.home)
        self.tabs.currentWidget().load(QUrl(self.home))
        currentIndex=self.tabs.currentIndex()
        self.status.showMessage(str("Last Action: Go Home on tab: " + str(currentIndex)))                

#Back function.
    def backs(self):	
        self.tabs.currentWidget().back()
        currentIndex=self.tabs.currentIndex()    
        self.status.showMessage(str("Last Action: Go Back on tab: " + str(currentIndex)))
                       		
#Forward function.	
    def forwards(self):	
        self.tabs.currentWidget().forward()
        currentIndex=self.tabs.currentIndex()        
        self.status.showMessage(str("Last Action: Go Forward on tab: " + str(currentIndex)))                
    
#Reload function.
    def reloads(self):	
        self.tabs.currentWidget().reload()
        currentIndex=self.tabs.currentIndex()        
        self.status.showMessage(str("Last Action: Reload Page on tab: " + str(currentIndex)))  
  
#Print functions  
    def handlePreview(self):
        dialog = QPrintPreviewDialog()
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()

    def handlePaintRequest(self, printer):
        self.tabs.currentWidget().render(QPainter(printer))	  

#####Page Zoom functions.   
    def zoomins(self):
        self.tabs.currentWidget().setZoomFactor(self.tabs.currentWidget().zoomFactor()+.2)
        currentIndex=self.tabs.currentIndex()
        self.status.showMessage(str("Last action: Zoomed in on tab: " + str(currentIndex)))

    def zoomouts(self):
        self.tabs.currentWidget().setZoomFactor(self.tabs.currentWidget().zoomFactor()-.2)
        currentIndex=self.tabs.currentIndex()
        self.status.showMessage(str("Last action: Zoomed out on tab: " + str(currentIndex)))
#####Search engines & default (Now. Startpage).
    def extra(self):
        search=self.Search.text()
        text=self.switch_2.text()
        if text == ('eco'):

#Ecosia search.
            adds1="https://www.ecosia.org/search?method=index&q=" + search 
            self.tabs.currentWidget().load(QUrl(adds1))
            print(adds1)
        
        elif text == ('wiki'):

#Wikipedia search (english).        
            adds1="https://en.wikipedia.org/w/index.php?title=Special:Search&profile=default&fulltext=Search&search=" + search 
            self.tabs.currentWidget().load(QUrl(adds1))
            print (adds1)

        elif text == ('tube'):

#Youtube search (english).        
            adds1="https://www.youtube.com/results?search_query=" + search 
            self.tabs.currentWidget().load(QUrl(adds1))
            print (adds1)

        elif text == ('gs'):

#Startpage search (english).        
            adds1="https://startpage.com/do/search?query=" + search 
            self.tabs.currentWidget().load(QUrl(adds1))
            print (adds1)

        else:
            adds1="https://startpage.com/do/search?query=" + search 
            self.tabs.currentWidget().load(QUrl(adds1))
            print (adds1)
       
#About messagebox.
    def about(self):
        buttonReply = QMessageBox.question(self, "RunIT-QT Browser Copyright (c) 2015 JJ Posti <techtimejourney.net>", "RunIT-QT  comes with ABSOLUTELY NO WARRANTY;  This is free software, and you are welcome to redistribute it under  GPL Version 2, June 1991 This is the 0.7  QWebEngineView version(July 2022). ___________________________________________________________________________ \n \nRight-click menu:Save image/page/object functionality:\n\nRight-click upon an image/page/object and choose Copy image/page/object address.\n \nNext choose Save image/page/object and the Save as dialog should open. \n \n", QMessageBox.Ok )
        if buttonReply == QMessageBox.Ok:
            pass       
             
          
class NewPage(QWebEnginePage):
    def __init__(self, parent=None):
        super(NewPage, self).__init__(parent)
          
    def userAgentForUrl(self, url):
        ''' Returns a User Agent that will be seen by the website. '''
        return "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    
    def triggerAction(self, action, checked=False):
        if action == QWebEnginePage.OpenLinkInNewWindow:
            self.createWindow(QWebEnginePage.WebBrowserWindow)
            
        if action == QWebEnginePage.SavePage:
            clipboard = QApplication.clipboard()
            http_location=str(clipboard.text())
            print ("Page location:" + http_location) 
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(None,"Save as","","All Files (*)", options=options)
            if fileName:
                subprocess.Popen(['wget', http_location, '-O', fileName])                                      

        elif action == QWebEnginePage.DownloadMediaToDisk:
            clipboard = QApplication.clipboard()
            http_location=str(clipboard.text())
            print ("Content location:" + http_location) 
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(None,"Save as","","All Files (*)", options=options)
            if fileName:
                subprocess.Popen(['wget', http_location, '-O', fileName])                                      

        elif action == QWebEnginePage.DownloadImageToDisk:
            clipboard = QApplication.clipboard()
            http_location=str(clipboard.text())
            print ("Image location:" + http_location) 
            options = QFileDialog.Options()
            options |= QFileDialog.DontUseNativeDialog
            fileName, _ = QFileDialog.getSaveFileName(None,"Save as","","All Files (*)", options=options)
            if fileName:
                subprocess.Popen(['wget', http_location, '-O', fileName])                                      
        return super(NewPage, self).triggerAction(action, checked)

class HtmlView(QWebEngineView):
    def __init__(self, *args, **kwargs):
        QWebEngineView.__init__(self, *args, **kwargs)
        self.tab = self.parent()  
        self.NewPage = NewPage(self)        
        self.setPage(self.NewPage)
        
    def createWindow(self, windowType):
        if windowType == QWebEnginePage.WebBrowserTab:
            webView = HtmlView(self.tab)
            ix = self.tab.tabs.addTab(webView, "Tab")
            self.tab.tabs.setCurrentIndex(ix)
            return webView    
        return QWebEngineView.createWindow(self, windowType)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    main = TabWidget()
    main.show()
    sys.exit(app.exec_())
