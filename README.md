# RunIT-QT (PyQt WebEngine Browser)

RunIT-QT is a tiny, privacy-leaning Qt WebEngine browser that aims to be **fast**, **low-memory**, and **simple**. It ships with a built-in host-level adblocker, HTTPS lock/certificate viewer, session restore, a minimal UI, and a streaming downloader that defaults to `~/Downloads`.

## License

RunIT-QT is licensed under **GPL v2** (June 1991).
RunIT-QT Browser Copyright (c) 2015 JJ Posti <techtimejourney.net>" 
RunIT-QT  comes with ABSOLUTELY NO WARRANTY;  This is free software, and you are welcome to redistribute it under  GPL Version 2, June 1991 

<img width="1773" height="1073" alt="Image" src="https://github.com/user-attachments/assets/e48a113b-3b1a-4bb0-b458-ce83ba8f0e6a" />


##### This is the 1.0 RC2 (November 2025).


---

## ✨ Highlights

- **Minimal UI**
  - Two toolbars (navigation + tools/search/zoom).
  - Tabbed browsing with last-tab protection.
  - Address bar that accepts both URLs and search terms.
  - Small “engine” box + search field (`gs`, `wiki`, `tube`).

- **Built-in Adblock (host + path hints)**
  - Uses a compact cache generated from several lists:
    - EasyList, EasyPrivacy, Fanboy Annoyances/Social, uBlock/uAssets, AdGuard, OISD, Peter Lowe, StevenBlack, URLHaus, HaGeZi.
  - Blocks by **host suffix** and a small set of **path hints** (e.g. `/ads`, `/analytics`) for subresources only (never blocks the main page).

- **YouTube / Media friendly**
  - HTML5 fullscreen support (toolbar/status auto-hidden, `Esc` exits).
  - Major Google/YouTube CDNs are always allowed (`googlevideo.com`, `ytimg.com`, etc.) to avoid breaking playback.

- **HTTPS lock + Certificate viewer**
  - 🔒/🔓 icon next to the URL bar reflects HTTP vs HTTPS.
  - Click it on HTTPS pages to show:
    - Subject CN
    - Issuer CN
    - Valid from / until dates.

- **Session restore**
  - Open tabs are saved to `~/.runit_qt_session.json` on exit and restored on next startup.

- **JavaScript & Images toggle**
  - “JS/Img ON” button toggles JavaScript and image loading for the profile and all existing tabs.

- **Zoom controls**
  - Toolbar buttons and shortcuts for zoom in/out/reset, with status-bar feedback.

- **Streaming downloader**
  - All downloads are routed through a small dialog window.
  - Defaults to `~/Downloads` as the target directory.
  - Automatically sanitizes filenames and can append an extension based on MIME type.
  - Uses a `.part` file and atomically renames on completion.
  - Warns before downloading potentially risky executable formats.

- **“Private-ish” defaults**
  - Tries to use a lean, off-the-record `QWebEngineProfile`:
    - No HTTP disk cache.
    - In-memory cookies only when possible.
    - Mixed content allowed by default (for real-world compatibility).

- **No `.pyc` clutter**
  - Bytecode generation is disabled (`sys.dont_write_bytecode = True`), so the project does not leave `__pycache__` around when run via `main.py` / `download.py`.

###### Notice: Adblock is on by default. You also need to click: <v> Allow this site </b> and possible make sure that <b> JS/Img is turned on ON </b> 
---

## 📦 Dependencies

### Runtime (Debian / Ubuntu)

The browser targets **Qt 6 + PyQt6**. On a Debian/Ubuntu-like system, you can install the needed libraries with:

```bash
# Qt 6 libraries (runtime + dev headers, useful if you build other Qt stuff)
sudo apt install   qt6-base-dev qt6-webengine-dev   libqt6webenginecore6 libqt6webenginewidgets6 libqt6widgets6

# Python bindings (PyQt6 + WebEngine + SVG)
sudo apt install   python3-pyqt6   python3-pyqt6.qtwebengine   python3-pyqt6.qtsvg
```

### Runtime (cross-platform via pip)

If your distro packages are old or you’re on another OS:

```bash
python3 -m pip install --upgrade pip

# Core Qt bindings
python3 -m pip install PyQt6

# WebEngine bindings (pulls in PyQt6-WebEngine-Qt6 subset of Qt)
python3 -m pip install PyQt6-WebEngine
```

The `PyQt6-WebEngine` package requires **Python 3.9+**.

### Optional: PyQt5

The code includes compatibility shims for **PyQt5 + QtWebEngine** (where available), but PyQt6 is the primary target.
Packages to install on PyQt5. Notice that the names might be different depending on your distribution:

sudo apt-get install -y \
 python3-pyqt5 \
 python3-pyqt5.qtwebengine \
 python3-pyqt5.qtsvg \
 python3-pyqt5.qtnetwork \
 python3-pyqt5.qtwebchannel \
 qtbase5-dev \
 qtwebengine5-dev \
 libqt5webenginewidgets5 \
 libqt5webenginecore5


---

## Quick Start

```bash
python3 main.py
```
#### On every launch, if cli is used: PyQt version data is printed.

On first launch:

- A **Home** tab opens at **Startpage** (`https://startpage.com`).
- The status bar briefly displays the Qt / PyQt version banner.
- The adblocker starts a background update if the local cache is stale.
---

## UI Basics

### Address bar

- Type a URL (`example.org`) or a full URL (`https://example.org`).
- Or just type text — it is sent to **Startpage** as a search.

### Mini search box

Two small fields on the second toolbar:

- **Engine code** (left box, defaults to `gs`):
  - `gs` / `start` / `sp` → Startpage  
  - `wiki` → English Wikipedia search  
  - `tube` / `yt` → YouTube search
- **Query** (right box): text to search for.

Press **Enter** in either box to search in the current tab.

### Toolbar buttons

Top row:

- **New Tab**
- **Back / Fwd**
- **Reload**
- **Home** (Startpage)
- **🔒 / 🔓** — connection security; click to view certificate info on HTTPS.

Second row:

- **Adblock ON / OFF** — global adblock toggle.
- **Allow this site** — per-site allow-list (suffix-based).
- **Update Lists** — force refresh of filter lists.
- **JS/Img ON / OFF** — enable/disable JavaScript and images.
- **Zoom − / 100% / Zoom +** — adjusts zoom for the current tab.

---

## ⌨️ Keyboard Shortcuts

- **Ctrl+T** — New tab.  
- **Ctrl+K** — Focus mini search box.  
- **Ctrl+Plus / Ctrl+Equals** — Zoom in.  
- **Ctrl+Minus** — Zoom out.  
- **Ctrl+0** — Reset zoom to 100%.  
- **Esc** — Exit fullscreen mode when a page has requested fullscreen.

---

## 🛡️ Adblock Details

- **What gets blocked?**
  - Only **subresources** (scripts, images, XHR, etc.) are blocked.
  - Main page navigations are never blocked.
  - Stylesheets and fonts are explicitly exempt to avoid “blank page with text links” issues.

- **Lists & cache**
  - On first run or when the cache is older than 7 days, RunIT-QT downloads and compiles several well-known filter lists into a lightweight cache file:
    ```text
    ~/.runit_qt_blockcache.json
    ```
  - The cache stores:
    - `hosts`: domains to block (as suffixes, e.g. `tracker.example.com`, `example.com`).  
    - `paths`: a capped set of short URL fragments (`/ads`, `/banner`, `/analytics`, …).

- **Force update**
  - Click **“Update Lists”** in the toolbar.
  - The status bar shows a “Updating adblock lists…” message; when done you’ll see something like:
    ```
    Adblock: N hosts, M hints
    ```
    and the log prints reload info.

- **CDN / media allow-list**
  - Domains such as `googlevideo.com`, `ytimg.com`, `fonts.gstatic.com`, major CDNs, and WordPress asset hosts are always allowed so pages don’t silently break.

- **Per-site allow-list**
  - “Allow this site” adds the current site’s registrable suffix (e.g. `example.com`) to a runtime allow-list inside the interceptor. Click again to remove it.

---

## 🔒 Security & Privacy

- **HTTPS lock**
  - 🔒 = HTTPS; 🔓 = not HTTPS.
  - Certificate dialog shows:
    - Subject CN
    - Issuer CN
    - Validity window (from / until).

- **Mixed content**
  - “Allow running insecure content” is enabled by default to avoid surprises with real-world sites that still embed HTTP content. You can change this in the code if you prefer strict HTTPS.

- **Profile longevity**
  - The WebEngine profile tries to be off-the-record (no cache path, no persistent storage path, no persistent cookies). Actual disk usage may still depend on the underlying Qt and OS.

---

## Downloads

All downloads are handled by `download.py` via a small streaming dialog:

- **Default directory:** `~/Downloads` (created if missing).
- **Sanitized filenames:** unsafe characters are replaced with `_`; leading dots are stripped; length is capped; Windows-reserved names are avoided.
- **Automatic extensions:** if the URL doesn’t contain a sensible filename, the downloader uses the HTTP `Content-Type` header to infer an extension (e.g. `application/pdf` → `.pdf`) and appends it when no extension is present.
- **Atomic writes:** data is streamed to a `*.part` file and flushed; once complete, the temporary file is atomically renamed to the final path.
- **Safety prompts:** executables and other risky formats (e.g. `.exe`, `.msi`, `.bat`, `.apk`, etc.) trigger a confirmation dialog before the download proceeds from the browser side.

You can also launch the downloader standalone:

```bash
python3 download.py
```

---

## Where Things Are Stored

- **Session file**
  - `~/.runit_qt_session.json`  
  - Stores the list of open tabs/URLs and is read back on startup.

- **Adblock cache**
  - `~/.runit_qt_blockcache.json`  
  - Contains compiled host/path data and metadata including last update time.

- **Downloads**
  - Default target directory: `~/Downloads` (configurable by editing `download.py`).

---

## File descriptions


```text
main.py        # Entry point; sets up QApplication + Browser window
qt_compat.py   # PyQt5 / PyQt6 compat layer and helpers
adblocker.py   # Blocklist fetching/parsing + TinyAdblockInterceptor
web_profile.py # Lean QWebEngineProfile factory
web_page.py    # SecurePage (navigation policy, permissions, JS console)
browser.py     # Main window (tabs, toolbars, session, downloads)
config.py      # App name, theme, and constants
download.py    # Streaming downloader dialog
README.md      # This file
```

---


