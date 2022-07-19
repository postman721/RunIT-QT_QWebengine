# RunIT-QT_QWebengine
RunIT Browser (QWebEngine version)

0.7 (July 2022) notable improvements/changes:

![new](https://user-images.githubusercontent.com/29865797/179807565-f323399c-5a49-4e30-8c21-c633abd6b64d.jpg)

- Youtube and Netflix confirmed working on almost complete full screen mode.

- Homepage is now pointing to StartPage search engine.

- Window is resized to be larger and more useful from the beginning.

- Addressbar improvements: google.com AND www.google.com AND https://google.com will resolve. -> https is auto appended into the front.

- More verbosity added to statusbar(notices go back, go forward etc. functions on tabs).

- UI is styled to be darker than before.

- Tabs now have titles in them.

- Back, forward etc. Now upgrade urlbar address like they should.

- Ecosia replaces Wolfram Alpha on search engines.



#### OLD VERSION CHANGELOGS

From 0.7 RC2 
Deprecating icons and increasing python3 compatibility.


![browser](https://user-images.githubusercontent.com/29865797/128581188-7023303a-a561-40bd-b37c-a82f4eaf9d23.png)


- Tabbed browsing: Double-click existing tab to get a new empty tab.
- Right-click: Open link in a new tab functionality is now working.
- More integrations to double-click menu. See about (i) for more information.
- QWebEngine capability integrations continue: code becomes a bit cleaner and more functional.
- UI is changed to become more clearer.
- Tabs are numbered. 
- Statusbar shows what was last loaded and on what tab.

TODO in upcoming releases: 

- Possibly integate label support as seen on previous releases.
- Enhance and integrate more QWebpage right-click functionalities.

	

Dependencies:

Something like below, should be enough.

python-pyqt5.qtwebengine python-pyqt5 ca-certificates


OR

python3-pyqt5.qtwebengine python3-pyqt5 ca-certificates



Remember to make the files executable with chmod +x some_file

Run the browser: python run.py 


_______________________________________
