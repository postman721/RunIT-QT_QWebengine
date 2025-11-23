# -*- coding: utf-8 -*-
"""
config.py — Global configuration, theme and small constants
for the RunIT-QT browser.
"""

APP_NAME = "RunIT-QT"

# Homepage & search defaults
HOME_URL = "https://startpage.com"

# Futuristic stylesheet used by the main window.
# This is copied from your original single-file script.
FUTURE_QSS = """
/* ======= FUTURISTIC THEME — ACCESSIBLE / HIGH-CONTRAST ======= */
/* Palette
   bg-deep:    #0B0F1A
   bg-panelA:  #0E1322
   bg-panelB:  #0F1527
   bg-field:   #0E1730
   text:       #C9D1D9
   text-strong:#E6EDF3
   text-muted: #9AA8BC
   text-disabled:#70819D
   stroke:     #223056
   stroke-2:   #1D2744
   accent:     #28C8FF
   accent-2:   #7C4DFF
*/

/* Avoid forcing white text everywhere; keep only typographic tweaks globally */
* {
    letter-spacing: 0.1px;
    font-weight: 500;
    background: #505356;
    color: #FFFFFF;
}
"""
