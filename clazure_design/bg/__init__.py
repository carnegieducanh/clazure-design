import os
import json
from pathlib import Path

from anki.utils import pointVersion
from aqt import mw, gui_hooks
from aqt.qt import QDir

from .adjust_css import (
    adjust_deckbrowser_css,
    adjust_toolbar_css,
    adjust_bottomtoolbar_css,
    adjust_overview_css,
    adjust_congrats_css,
    adjust_reviewer_css,
    adjust_reviewerbottom_css,
)
from .config import addon_path, addonfoldername, gc

QDir.addSearchPath("CustomBackground", str(Path(__file__).parent / "AnKing"))

css_folder_for_anki_version = {
    "22": "22", "23": "22", "24": "22",
    "25": "25", "26": "25", "27": "25", "28": "25", "29": "25",
    "30": "25", "31": "31", "32": "31", "33": "31", "34": "31",
    "35": "31", "36": "36", "37": "36", "38": "36", "39": "36",
    "40": "36", "41": "36", "42": "36", "43": "36", "44": "36",
    "45": "36", "46": "36", "47": "36", "48": "36", "49": "36",
    "50": "36", "51": "36", "52": "36", "53": "36", "54": "36",
    "55": "55",
}
v = str(pointVersion())
if v in css_folder_for_anki_version:
    version_folder = css_folder_for_anki_version[v]
else:
    version_folder = css_folder_for_anki_version[max(css_folder_for_anki_version, key=int)]

regex = r"(bg/user_files.*|bg/web.*)"
mw.addonManager.setWebExports(__name__, regex)

css_files_to_modify = [
    "webview.css", "deckbrowser.css", "overview.css", "reviewer-bottom.css",
    "toolbar-bottom.css", "reviewer.css", "toolbar.css",
]


def maybe_adjust_filename_for_2136(filename):
    if pointVersion() >= 36:
        filename = filename.lstrip("css/")
    return filename


def reset_background(new_state, old_state):
    if new_state == "deckBrowser":
        mw.deckBrowser.show()
        if pointVersion() >= 27:
            mw.toolbar.draw()


gui_hooks.state_did_change.append(reset_background)


def inject_css(web_content, context):
    for filename in web_content.css.copy():
        filename = maybe_adjust_filename_for_2136(filename)
        if filename in css_files_to_modify:
            web_content.css.append(
                f"/_addons/{addonfoldername}/bg/web/css/{version_folder}/{filename}"
            )
            web_content.css.append(
                f"/_addons/{addonfoldername}/bg/user_files/css/custom_{filename}"
            )

        css = ""
        if filename == "deckbrowser.css":
            css = adjust_deckbrowser_css()
        if filename == "toolbar.css" and gc("Toolbar image"):
            css = adjust_toolbar_css()
        if filename == "overview.css":
            css = adjust_overview_css()
        if filename == "toolbar-bottom.css" and gc("Toolbar image"):
            css = adjust_bottomtoolbar_css()
        if filename == "reviewer.css" and gc("Reviewer image"):
            css = adjust_reviewer_css()
        if filename == "reviewer-bottom.css":
            if v == "22":
                if gc("Reviewer image") and gc("Toolbar image"):
                    css = adjust_reviewerbottom_css()
            else:
                css = adjust_reviewerbottom_css()
        if css:
            web_content.head += f"<style>{css}</style>"


def inject_css_into_ts_page(web):
    page = os.path.basename(web.page().url().path())
    if page not in ("congrats.html", "congrats"):
        return
    css = adjust_congrats_css()
    web.eval(
        """
(() => {
    const style = document.createElement("style");
    style.textContent = %s;
    document.head.appendChild(style);
})();
"""
        % json.dumps(css)
    )


gui_hooks.webview_will_set_content.append(inject_css)
gui_hooks.webview_did_inject_style_into_page.append(inject_css_into_ts_page)
