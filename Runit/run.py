#RunIT-QT Browser Copyright (c) 2015 JJ Posti <techtimejourney.net> 
#RunIT-QT  comes with ABSOLUTELY NO WARRANTY; 
#for details see: http://www.gnu.org/copyleft/gpl.html. 
#This is free software, and you are welcome to redistribute it under 
#GPL Version 2, June 1991
#This is the 0.7 version(May 2018)
#This version uses QWebEngine

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *
from icons import *
import os, sys, subprocess
from subprocess import Popen 


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

#Lets apply overall general style for now.
        self.setStyleSheet("*{color:#ffffff; background-color:#232323; border: 2px solid #232323; border-radius: 4px;font-size: 14px;}"
        "*:hover{background-color:#5c5c5c;}")

#Tabs window.

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)

#Toolbar.      
        self.toolbar = QToolBar("Navigation")
        self.toolbar.setIconSize(QSize(22, 22))
        self.toolbar.setStyleSheet("QToolBar{color:#ffffff; background-color:#232323; border: 2px solid #353535; border-radius: 6px;font-size: 14px;}"
        "QToolBar:hover{background-color:#5c5c5c;}") 
        self.addToolBar(self.toolbar)


#Back.        
        self.back = QToolButton()
        self.back.setStyleSheet("QToolButton{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        icon = QIcon()
        icon.addPixmap(QPixmap((":/icons/back.png")), QIcon.Normal, QIcon.Off)
        self.back.setIcon(icon)
        self.back.setToolTip('Go Back')
        self.back.clicked.connect(self.backs)
        self.back.setFixedSize(24, 24)
        self.toolbar.addWidget(self.back)
     

#Forward.        
        self.forward = QToolButton()
        self.forward.setStyleSheet("QToolButton{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        icon1 = QIcon()
        icon1.addPixmap(QPixmap((":/icons/forward.png")), QIcon.Normal, QIcon.Off)
        self.forward.setIcon(icon1)
        self.forward.setToolTip('Go Forward')
        self.forward.clicked.connect(self.forwards)
        self.forward.setFixedSize(24, 24)
        self.toolbar.addWidget(self.forward)


#Reload.        
        self.reloading = QToolButton()
        self.reloading.setStyleSheet("QToolButton{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        icon3 = QIcon()
        icon3.addPixmap(QPixmap((":/icons/reload.png")), QIcon.Normal, QIcon.Off)
        self.reloading.setIcon(icon3)
        self.reloading.setToolTip('Reload Page')
        self.reloading.clicked.connect(self.reloads)
        self.reloading.setFixedSize(24, 24)
        self.toolbar.addWidget(self.reloading)

#Home.        
        self.home = QToolButton()
        self.home.setStyleSheet("QToolButton{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        icon2 = QIcon()
        icon2.addPixmap(QPixmap((":/icons/home.png")), QIcon.Normal, QIcon.Off)
        self.home.setIcon(icon2)
        self.home.setToolTip('Go Home')
        self.home.clicked.connect(self.homes)
        self.home.setFixedSize(24, 24)
        self.toolbar.addWidget(self.home)


#Printing.        
        self.printing = QToolButton()
        self.printing.setStyleSheet("QToolButton{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        icon8 = QIcon()
        icon8.addPixmap(QPixmap((":/icons/print.png")), QIcon.Normal, QIcon.Off)
        self.printing.setIcon(icon8)
        self.printing.setObjectName(("print"))
        self.printing.setToolTip('Print')
        self.printing.clicked.connect(self.handlePreview)
        self.printing.setFixedSize(24, 24)
        self.toolbar.addWidget(self.printing)

#Addressbar.       
        self.address = QLineEdit()
        self.address.setStyleSheet("QLineEdit{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QLineEdit:hover{background-color:#5c5c5c;}") 
        self.address.setPlaceholderText("Type an address")
        self.address.returnPressed.connect(self.system_arguments)
        self.toolbar.addWidget(self.address)
        self.add_new_tab(QUrl('https://www.techtimejourney.net/audax'), 'PostX Gnu/Linux')
        self.show()

#Html5 player.        
        self.html = QToolButton()
        self.html.setStyleSheet("QToolButton{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        icon4 = QIcon()
        icon4.addPixmap(QPixmap((":/icons/vlc_play.png")), QIcon.Normal, QIcon.Off)
        self.html.setIcon(icon4)
        self.html.setObjectName(("Html5 player"))
        self.html.setToolTip('HTML5 player')
        self.html.clicked.connect(self.html5)
        self.html.setFixedSize(24, 24)
        self.toolbar.addWidget(self.html)       

#Zoom +.       
        self.zoom_in = QToolButton()
        self.zoom_in.setStyleSheet("QToolButton{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        icon9 = QIcon()
        icon9.addPixmap(QPixmap((":/icons/zoom-in.png")), QIcon.Normal, QIcon.Off)
        self.zoom_in.setIcon(icon9)
        self.zoom_in.setObjectName(("zoom_in"))
        self.zoom_in.setToolTip('Zoom +')
        self.zoom_in.clicked.connect(self.zoomins)
        self.zoom_in.setFixedSize(24, 24)
        self.toolbar.addWidget(self.zoom_in)

#Zoom -.        
        self.zoom_out = QToolButton()
        self.zoom_out.setStyleSheet("QToolButton{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        icon10 = QIcon()
        icon10.addPixmap(QPixmap((":/icons/zoom-out.png")), QIcon.Normal, QIcon.Off)
        self.zoom_out.setIcon(icon10)
        self.zoom_out.setObjectName(("zoom_out"))
        self.zoom_out.setToolTip('Zoom -')
        self.zoom_out.clicked.connect(self.zoomouts)
        self.zoom_out.setFixedSize(24, 24)
        self.toolbar.addWidget(self.zoom_out)


#Printing.        
        self.printing = QToolButton()
        self.printing.setStyleSheet("QToolButton{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        icon8 = QIcon()
        icon8.addPixmap(QPixmap((":/icons/print.png")), QIcon.Normal, QIcon.Off)
        self.printing.setIcon(icon8)
        self.printing.setToolTip('Print')
        self.printing.clicked.connect(self.handlePreview)
        self.printing.setFixedSize(24, 24)
        self.toolbar.addWidget(self.printing)

####################
#Search engine parts
####################

#Search Switch.        
        self.switch_2 = QLineEdit()
        self.switch_2.setStyleSheet("QLineEdit{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QLineEdit:hover{background-color:#5c5c5c;}") 
        self.switch_2.setObjectName(("switch_2"))
        self.switch_2.setPlaceholderText("Switch")
        self.switch_2.setFixedSize(50, 24)
        self.switch_2.setToolTip('st=Startpage, wiki = Wikipedia,  tube = Youtube,  wolf = Wolfram Alpha. Empty = Startpage search (default)')
        self.switch_2.returnPressed.connect(self.extra)
        self.toolbar.addWidget(self.switch_2)

#Search.        
        self.Search = QLineEdit()
        self.Search.setStyleSheet("QLineEdit{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QLineEdit:hover{background-color:#5c5c5c;}") 
        self.Search.setPlaceholderText("Search")
        self.Search.setToolTip('Search')
        self.Search.returnPressed.connect(self.extra)
        self.toolbar.addWidget(self.Search)


#About.
        self.about1 = QPushButton()
        self.about1.setObjectName("Info")
        self.about1.setStyleSheet("QPushButton{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QPushButton:hover{background-color:#5c5c5c;}") 
        self.about1.setText("i")
        self.about1.setToolTip('Info')
        self.about1.setFixedSize(24, 24)
        self.about1.clicked.connect(self.about) 
        self.toolbar.addWidget(self.about1)
                
#Browser settings.
        self.browser.page().settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self.browser.page().settings().setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        self.browser.page().settings().setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, True)
        self.browser.page().settings().setAttribute(QWebEngineSettings.LocalStorageEnabled, True)
        self.browser.page().settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.browser.page().settings().setAttribute(QWebEngineSettings.SpatialNavigationEnabled, True)
        self.browser.page().settings().setAttribute(QWebEngineSettings.AutoLoadImages, True)

      
###############################################################
#Bookmark.        
        self.bookmark = QToolButton()
        self.bookmark.setStyleSheet("QToolButton{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        icon5 = QIcon()
        icon5.addPixmap(QPixmap((":/icons/bookmark.png")), QIcon.Normal, QIcon.Off)
        self.bookmark.setIcon(icon5)
        self.bookmark.setObjectName(("bookmark"))
        self.bookmark.setToolTip('Bookmark addressbar location')
        self.bookmark.clicked.connect(self.bookmarks)
        self.bookmark.setFixedSize(24, 24)
        self.toolbar.addWidget(self.bookmark)

#Open Bookmarks.        
        self.see_bookmark = QToolButton()
        self.see_bookmark.setStyleSheet("QToolButton{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        icon6 = QIcon()
        icon6.addPixmap(QPixmap((":/icons/seebook.png")), QIcon.Normal, QIcon.Off)
        self.see_bookmark.setIcon(icon6)
        self.see_bookmark.setObjectName(("see_bookmark"))
        self.see_bookmark.setToolTip('See Bookmarks')
        self.see_bookmark.clicked.connect(self.bookopen)
        self.see_bookmark.setFixedSize(24, 24)
        self.toolbar.addWidget(self.see_bookmark)
        
#Download.        
        self.download = QToolButton()
        self.download.setStyleSheet("QToolButton{color:#ffffff; background-color:#353535; border: 2px solid #353535; border-radius: 3px;font-size: 12px;}"
        "QToolButton:hover{background-color:#5c5c5c;}") 
        icon7 = QIcon()
        icon7.addPixmap(QPixmap((":/icons/download.png")), QIcon.Normal, QIcon.Off)
        self.download.setIcon(icon7)
        self.download.setObjectName(("download"))
        self.download.setToolTip('Download file from location')
        self.download.clicked.connect(self.downloads)
        self.download.setFixedSize(24, 24)
        self.toolbar.addWidget(self.download)        
#############################################################
                
#Tab / WebView setup
    def add_new_tab(self, qurl=None, label="Blank"):
        if qurl is None:
            qurl = QUrl('')

        self.browser = QWebEngineView()
        self.browser.setUrl(qurl)
        i = self.tabs.addTab(self.browser, label)

        self.tabs.setCurrentIndex(i)

        self.browser.urlChanged.connect(lambda qurl, browser=self.browser:
                                   self.update_address(qurl, self.browser))

        self.browser.loadFinished.connect(lambda _, i=i, browser=self.browser:
                                     self.tabs.setTabText(i, self.browser.page().title()))

    def tab_open_doubleclick(self, i):
        if i == -1: 
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_address(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def update_title(self, browser):
        if self.browser != self.tabs.currentWidget():
            return
        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("%s  RunIT Browser" % title)

    def update_address(self, q, browser=None):

        if self.browser != self.tabs.currentWidget():
            return
        self.address.setText(q.toString())
        self.address.setCursorPosition(0)
######################################################

#####Download functions.

    def downloads(self):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self.browser,"Save as","","All Files (*)", options=options)
        address=self.address.text()
        if fileName:
            subprocess.Popen(['wget', address, '-O', fileName])

#####Printer functions.

    def handlePreview(self):
        dialog = QPrintPreviewDialog()
        dialog.paintRequested.connect(self.handlePaintRequest)
        dialog.exec_()

    def handlePaintRequest(self, printer):
        self.browser.render(QPainter(printer))	

#####Page navigation functions.

#Home page function.
    def homes(self):
        self.home = "http://www.techtimejourney.net/audax"
        self.address.setText(self.home)
        self.browser.load_uri(QUrl(self.home))
        
#Back function.
    def backs(self,url):
        goback=self.browser.back()
	
#Forward function.	
    def forwards(self,url):	
        self.browser.forward()       

#Reload function.
    def reloads(self):	
        self.browser.reload()

#About messagebox.
    def about(self):
        buttonReply = QMessageBox.question(self, "RunIT-QT Browser Copyright (c) 2015 JJ Posti <techtimejourney.net>", "RunIT-QT  comes with ABSOLUTELY NO WARRANTY;  This is free software, and you are welcome to redistribute it under  GPL Version 2, June 1991 This is the 0.7 version(May 2018). ___________________________________________________________________________ \n \nArgument support:\nStart browser like this: runit 'google.fi' and select statusbar and then press Enter to navigate to the address you gave in arguments. ___________________________________________________________________________\n \nFind text from html:\nWrite find:something to address field and press enter to find the first entry. Press enter again to find the second entry etc. ___________________________________________________________________________\n \nSave images or files functionality: Right-click upon an image and choose Copy Image URL. Paste the url to the addressbar.  Next click the Download button from toolbar and the Save as dialog should open.", QMessageBox.Ok )
        if buttonReply == QMessageBox.Ok:
            pass         
#############################

#Home page function.
    def homes(self):
        self.home = "http://www.techtimejourney.net/postx_pages/postx.html"
        self.address.setText(self.home)
        self.browser.load(QUrl(self.home))

#Page Zoom functions.
   
    def zoomins(self):
        self.browser.setZoomFactor(self.browser.zoomFactor()+.2)

    def zoomouts(self):
        self.browser.setZoomFactor(self.browser.zoomFactor()-.2)


#System arguments support / Go to address / Find text functionality.         
    def system_arguments(self):            
        if len(sys.argv) == 1:
            url=self.address.text()
            if url.startswith('http://'):
                change=str(url)
                self.address.setText(change)
                load=self.address.text()
                self.browser.load(QUrl(load))
                del sys.argv[1:]
        
            elif url.startswith('https://'):
                change=str(url)
                self.address.setText(change)
                load=self.address.text()
                self.browser.load(QUrl(load))
                del sys.argv[1:]
            
            elif url.startswith('find:'):
                load=self.address.text()
                self.result0 = load.replace('find:', '')
                print "Finding:" + self.result0                
                self.browser.findText(self.result0)
                del sys.argv[1:]

            else:
                add="https://" + url
                change=str(add)
                self.address.setText(change)
                load=self.address.text()
                self.browser.load(QUrl(load))
                del sys.argv[1:]
        
        else:    			        
             self.location = sys.argv[1:]
             self.temp=str(self.location)
             self.result0 = self.temp.replace('[', '')
             self.result1 = self.result0.replace(']', '')
             self.result_final = self.result1.replace("'", '')

             url=self.result_final
             if url.startswith('http://'):
                 change=str(url)
                 self.address.setText(change)
                 load=self.address.text()
                 self.loading1=self.browser.load(QUrl(load))
                 del sys.argv[1:]
                 
             elif url.startswith('https://'):
                  change=str(url)
                  self.address.setText(change)
                  load=self.address.text()
                  self.loading1=self.browser.load(QUrl(load))
                  del sys.argv[1:]

             else:
                  change=str("https://" + url)
                  self.address.setText(change)
                  load=self.address.text()
                  self.browser.load(QUrl(load))
                  del sys.argv[1:]
                  
#Open html5 playback. 
    def html5(self):
        subprocess.Popen(['python', '/usr/share/html5.py'])
#############################################
#Search engines
#############################################

#####Search engines & default (Now. Startpage).
    def extra(self):
        search=self.Search.text()
        text=self.switch_2.text()
        if text == ('wolf'):

#Wolfram Alpha search.
            adds1="https://www.wolframalpha.com/input/?i=" + search 
            self.browser.load(QUrl(adds1))
            print adds1
        
        elif text == ('wiki'):

#Wikipedia search (english).        
            adds1="https://en.wikipedia.org/w/index.php?title=Special:Search&profile=default&fulltext=Search&search=" + search 
            self.browser.load(QUrl(adds1))
            print adds1

        elif text == ('tube'):

#Youtube search (english).        
            adds1="https://www.youtube.com/results?search_query=" + search 
            self.browser.load(QUrl(adds1))
            print adds1

        elif text == ('st'):

#Startpage search (english).        
            adds1="https://startpage.com/do/search?query=" + search 
            self.browser.load(QUrl(adds1))
            print adds1

        else:
            adds1="https://startpage.com/do/search?query=" + search 
            self.browser.load(QUrl(adds1))
            print adds1                  


#####Bookmark functions.
    
    def bookmarks(self,widget):
        home=os.getenv("HOME")
        print home
        site=str(self.address.text())
        os.chdir(home) 
        f = open('.bookmarks.html', 'a')
        f.write("<br>" + "<a href=" + site + ">"+ site + "</a>")
        f.close()

#Open bookmarks file.
    def bookopen(self,widget):
    	home=os.getenv("HOME")
        print home
        home=os.getenv("HOME")
        os.chdir(home)
        head="file:///"
        books=".bookmarks.html"
        adds=self.address.setText(head + home + '/' + books)
        adda=self.address.text()
        self.browser.load(QUrl(adda))


app = QApplication(sys.argv)
app.setApplicationName("RunIT Browser")
window = MainWindow()
app.exec_()
