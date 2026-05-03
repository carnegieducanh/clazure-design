_MINIMAL_CSS = """\
/* Prettify by @pranavdeshai: Minimal — Version 0.1.3 */

/* -------------------------------------------------- PREFERENCES */
:root {
  --card-max-width: 40em;
  --card-text-align: left;
  --font-size-regular: 16px;
  --font-size-small: 14px;
  --font-family: "Inter", -apple-system, sytem-ui, BlinkMacSystemFont, Segoe UI,
    Roboto, Helvetica, Arial, sans-serif;
  --img-width: 50%;
  --img-brightness: 0.75;
  --img-filter: none;
}

/* -------------------------------------------------- COLORS */
.card {
  background-color: #E1D8C4;
  --text-fg: #333333e6;
  --text-fg-faint: #333333cc;
  --text-bg-selected: #3333331a;
  --card-bg: #F5EFDF;
  --card-border: #f7f7f7;
  --card-box-shadow: #3c42570f;
  --divider: #3333331a;
  --tag-fg: #333333cc;
  --tag-bg: #3333330f;
  --tag-fg-active: #333333;
  --tag-bg-active: #3333331a;
  --tag-border: transparent;
  --cloze-fg: #348ccb;
  --cloze-bg: transparent;
  --link-fg: #2a70a2;
  --link-bg: transparent;
  --link-fg-active: #2f7eb6;
  --link-bg-active: transparent;
  --bold-fg: var(--text-fg);
  --italic-fg: var(--text-fg);
  --bold-italic-fg: var(--text-fg);
  --underline-fg: var(--text-fg);
}

.card.night_mode {
  background-color: #242426;
  --text-fg: #ffffffe6;
  --text-fg-faint: #ffffffb3;
  --text-bg-selected: #ffffff1f;
  --card-bg: #2A2B2D;
  --card-border: #ffffff0a;
  --card-box-shadow: #0000001f;
  --divider: #ffffff1f;
  --tag-fg: #ffffffb3;
  --tag-bg: #ffffff14;
  --tag-fg-active: #ffffff;
  --tag-bg-active: #ffffff1f;
  --tag-border: transparent;
  --cloze-fg: #99ebff;
  --cloze-bg: transparent;
  --link-fg: #5da3d5;
  --link-bg: transparent;
  --link-fg-active: #71afda;
  --link-bg-active: transparent;
  --bold-fg: var(--text-fg);
  --italic-fg: var(--text-fg);
  --bold-italic-fg: var(--text-fg);
  --underline-fg: var(--text-fg);
}

/* -------------------------------------------------- BACKGROUND */
.card {
  cursor: default;
  padding: 0.5em 0;
}
html:not(.mobile) .card {
  padding: 0.5em;
}
.card::-webkit-scrollbar {
  display: none;
}

/* -------------------------------------------------- FLASHCARD */
.prettify-flashcard {
  background-color: var(--card-bg);
  border-radius: 1em;
  border: 1px solid var(--card-border);
  box-shadow: var(--card-box-shadow) 0px 7px 14px 0px, var(--card-box-shadow) 0px 3px 6px 0px;
  color: var(--text-fg);
  font-family: var(--font-family);
  font-size: var(--font-size-regular);
  line-height: 1.5;
  margin: 0 auto;
  max-width: var(--card-max-width);
  text-align: var(--card-text-align);
  word-wrap: break-word;
}
.prettify-flashcard ::selection {
  background-color: var(--text-bg-selected);
}

/* -------------------------------------------------- FIELDS */
.prettify-field {
  margin: 2em;
}
.mobile .prettify-field {
  margin: 1em;
}

.prettify-field--back {
  color: var(--text-fg-faint);
  font-size: var(--font-size-small);
}

/* -------------------------------------------------- CLOZE */
.cloze {
  background-color: var(--cloze-bg);
  color: var(--cloze-fg);
}

/* -------------------------------------------------- DECK */
.prettify-deck {
  margin: 2em;
  display: flex;
  color: var(--text-fg-faint);
  font-size: var(--font-size-small);
  white-space: nowrap;
}
.mobile .prettify-deck {
  margin: 1em;
}

.prettify-subdeck {
  text-decoration: underline;
  text-overflow: ellipsis;
  overflow: hidden;
}

/* -------------------------------------------------- TAGS */
.prettify-tags {
  margin: 2em;
  display: flex;
  flex-flow: row wrap;
  font-size: var(--font-size-small);
}
.mobile .prettify-tags {
  margin: 1em;
}

.prettify-tag {
  all: initial;
  background-color: var(--tag-bg);
  border-radius: 0.2em;
  color: var(--tag-fg);
  display: inline;
  font-size: var(--font-size-small);
  font-family: var(--font-family);
  margin: 0 0.5em 0.5em 0;
  padding: 0.25em;
  transition: all 0.25s;
  word-break: break-word;
}
.prettify-tag:hover {
  background-color: var(--tag-bg-active);
  color: var(--tag-fg-active);
  cursor: pointer;
}

/* -------------------------------------------------- DIVIDER */
.prettify-divider {
  background-color: transparent;
  border: none;
  border-bottom: 1px dashed var(--divider);
  margin: 1em;
  padding: 0;
}

.prettify-divider--answer {
  margin: 0 0 1em;
}

/* -------------------------------------------------- IMAGES */
img {
  border-radius: 0.25em;
  display: block;
  margin: 1em auto;
  max-width: var(--img-width) !important;
}
.night_mode img {
  filter: var(--img-filter);
  opacity: var(--img-brightness);
}
img + br {
  display: none;
}

/* -------------------------------------------------- TABLES */
table {
  border-collapse: separate;
  border-spacing: 0;
  margin: 0 auto;
  max-width: 100%;
}
table thead {
  background-color: var(--card-border);
}
table tr:nth-of-type(even) {
  background-color: var(--card-border);
}
table tr:first-child th:first-child { border-top-left-radius: 0.25em; }
table tr:first-child th:last-child  { border-top-right-radius: 0.25em; }
table tr:last-child td:first-child  { border-bottom-left-radius: 0.25em; }
table tr:last-child td:last-child   { border-bottom-right-radius: 0.25em; }
table th {
  border-bottom: solid 1px var(--text-bg-selected);
  border-left: solid 1px var(--text-bg-selected);
  border-top: solid 1px var(--text-bg-selected);
  padding: 0.5em;
}
table th:last-child { border-right: solid 1px var(--text-bg-selected); }
table td {
  border-bottom: solid 1px var(--text-bg-selected);
  border-left: solid 1px var(--text-bg-selected);
  padding: 0.5em;
}
table td:last-of-type { border-right: solid 1px var(--text-bg-selected); }

/* -------------------------------------------------- HYPERLINKS */
a, a:visited {
  text-decoration: none;
  color: var(--link-fg);
}
a:hover, a:active {
  text-decoration: underline;
  color: var(--link-fg-active);
}

/* -------------------------------------------------- FORMATTING */
b { color: var(--bold-fg); }
i { color: var(--italic-fg); }
b > i, i > b { color: var(--bold-italic-fg); }
u { color: var(--underline-fg); }
pre { white-space: normal; }

/* -------------------------------------------------- CUSTOM FONTS */
@font-face {
  font-family: Inter;
  src: local("Inter-Regular"), url("_Inter-Regular.woff2") format("woff2");
  font-style: normal;
  font-weight: normal;
  font-display: swap;
}
@font-face {
  font-family: Inter;
  src: local("Inter-Bold"), url("_Inter-Bold.woff2") format("woff2");
  font-style: normal;
  font-weight: bold;
  font-display: swap;
}
@font-face {
  font-family: Inter;
  src: local("Inter-Italic"), url("_Inter-Italic.woff2") format("woff2");
  font-style: italic;
  font-weight: normal;
  font-display: swap;
}
@font-face {
  font-family: Inter;
  src: local("Inter-BoldItalic"), url("_Inter-BoldItalic.woff2") format("woff2");
  font-style: italic;
  font-weight: bold;
  font-display: swap;
}
"""

_NORD_CSS = """\
/* Prettify by @pranavdeshai: Nord — Version 0.1.3 */

/* -------------------------------------------------- PREFERENCES */
:root {
  --card-max-width: 40em;
  --card-text-align: left;
  --font-size-regular: 16px;
  --font-size-small: 14px;
  --font-family: "Rubik", -apple-system, sytem-ui, BlinkMacSystemFont, Segoe UI,
    Roboto, Helvetica, Arial, sans-serif;
  --img-width: 50%;
  --img-brightness: 1;
  --img-filter: none;
}

/* -------------------------------------------------- COLORS */
.card {
  background-color: #ececec;
  --text-fg: #434c5e;
  --text-fg-faint: #4c566a;
  --text-bg-selected: #eceff4;
  --card-bg: #ffffff;
  --card-border: transparent;
  --card-box-shadow: #b8c2d740;
  --divider: #d8dee9;
  --tag-fg: #4c566a;
  --tag-bg: transparent;
  --tag-fg-active: #8fbcbb;
  --tag-bg-active: transparent;
  --tag-border: #d8dee9;
  --tag-border-active: #8fbcbb;
  --cloze-fg: #88c0d0;
  --cloze-bg: transparent;
  --link-fg: #81a1c1;
  --link-bg: transparent;
  --link-fg-active: #8fbcbb;
  --link-bg-active: #eceff4;
  --bold-fg: #bf616a;
  --italic-fg: #ebcb8b;
  --bold-italic-fg: #d08770;
  --underline-fg: #a3be8c;
}

.card.night_mode {
  background-color: #242933;
  --text-fg: #e7e9f0;
  --text-fg-faint: #d8dee9;
  --text-bg-selected: #3b4252;
  --card-bg: #2B313C;
  --card-border: transparent;
  --card-box-shadow: #0f111540;
  --divider: #4c566a;
  --tag-fg: #d8dee9;
  --tag-bg: transparent;
  --tag-fg-active: #8fbcbb;
  --tag-bg-active: transparent;
  --tag-border: #4c566a;
  --tag-border-active: #8fbcbb;
  --cloze-fg: #88c0d0;
  --cloze-bg: transparent;
  --link-fg: #81a1c1;
  --link-bg: transparent;
  --link-fg-active: #8fbcbb;
  --link-bg-active: #434c5e;
  --bold-fg: #bf616a;
  --italic-fg: #ebcb8b;
  --bold-italic-fg: #d08770;
  --underline-fg: #a3be8c;
}

/* -------------------------------------------------- BACKGROUND */
.card {
  cursor: default;
  padding: 0.5em 0;
}
html:not(.mobile) .card {
  padding: 0.5em;
}
.card::-webkit-scrollbar {
  display: none;
}

/* -------------------------------------------------- FLASHCARD */
.prettify-flashcard {
  background-color: var(--card-bg);
  border-radius: 1em;
  border: 1px solid var(--card-border);
  box-shadow: var(--card-box-shadow) 0px 4px 6px;
  color: var(--text-fg);
  font-family: var(--font-family);
  font-size: var(--font-size-regular);
  line-height: 1.5;
  margin: 0 auto;
  max-width: var(--card-max-width);
  text-align: var(--card-text-align);
  word-wrap: break-word;
}
.prettify-flashcard ::selection {
  background-color: var(--text-bg-selected);
}

/* -------------------------------------------------- FIELDS */
.prettify-field {
  margin: 2em;
}
.mobile .prettify-field {
  margin: 1em;
}

.prettify-field--back {
  color: var(--text-fg-faint);
  font-size: var(--font-size-small);
}

/* -------------------------------------------------- CLOZE */
.cloze {
  background-color: var(--cloze-bg);
  color: var(--cloze-fg);
}

/* -------------------------------------------------- DECK */
.prettify-deck {
  margin: 2em;
  display: flex;
  color: var(--text-fg-faint);
  font-size: var(--font-size-small);
  white-space: nowrap;
}
.mobile .prettify-deck {
  margin: 1em;
}

.prettify-subdeck {
  text-decoration: underline;
  text-overflow: ellipsis;
  overflow: hidden;
}

/* -------------------------------------------------- TAGS */
.prettify-tags {
  margin: 2em;
  display: flex;
  flex-flow: row wrap;
  font-size: var(--font-size-small);
}
.mobile .prettify-tags {
  margin: 1em;
}

.prettify-tag {
  all: initial;
  background-color: var(--tag-bg);
  border-radius: 0.25em;
  border: 1px solid var(--tag-border);
  color: var(--tag-fg);
  display: inline;
  font-size: var(--font-size-small);
  font-family: var(--font-family);
  font-style: italic;
  margin: 0 0.5em 0.5em 0;
  padding: 0.25em;
  transition: all 0.25s;
  word-break: break-word;
}
.prettify-tag:hover {
  background-color: var(--tag-bg-active);
  border: 1px solid var(--tag-border-active);
  color: var(--tag-fg-active);
  cursor: pointer;
}

/* -------------------------------------------------- DIVIDER */
.prettify-divider {
  background-color: transparent;
  border: none;
  border-bottom: 1px dashed var(--divider);
  margin: 1em;
  padding: 0;
}

.prettify-divider--answer {
  border-bottom: 1px solid var(--divider);
}

/* -------------------------------------------------- IMAGES */
img {
  border-radius: 0.25em;
  display: block;
  margin: 1em auto;
  max-width: var(--img-width) !important;
}
.night_mode img {
  filter: var(--img-filter);
  opacity: var(--img-brightness);
}
img + br {
  display: none;
}

/* -------------------------------------------------- TABLES */
table {
  border-collapse: separate;
  border-spacing: 0;
  margin: 0 auto;
  max-width: 100%;
}
table thead {
  background-color: var(--text-bg-selected);
}
table tr:nth-of-type(even) {
  background-color: var(--text-bg-selected);
}
table tr:first-child th:first-child { border-top-left-radius: 0.5em; }
table tr:first-child th:last-child  { border-top-right-radius: 0.5em; }
table tr:last-child td:first-child  { border-bottom-left-radius: 0.5em; }
table tr:last-child td:last-child   { border-bottom-right-radius: 0.5em; }
table th {
  border-bottom: solid 1px var(--card-border);
  border-left: solid 1px var(--card-border);
  border-top: solid 1px var(--card-border);
  padding: 0.5em;
}
table th:last-child { border-right: solid 1px var(--card-border); }
table td {
  border-bottom: solid 1px var(--card-border);
  border-left: solid 1px var(--card-border);
  padding: 0.5em;
}
table td:last-of-type { border-right: solid 1px var(--card-border); }

/* -------------------------------------------------- HYPERLINKS */
a, a:visited {
  text-decoration: none;
  color: var(--link-fg);
  border-radius: 0.25em;
  padding: 0 0.1em;
  transition: all 0.1s;
}
a:hover, a:active {
  color: var(--link-fg-active);
  background-color: var(--link-bg-active);
}

/* -------------------------------------------------- FORMATTING */
b, strong { color: var(--bold-fg); }
i, em     { color: var(--italic-fg); }
b > i, i > b { color: var(--bold-italic-fg); }
u { color: var(--underline-fg); }
pre { white-space: normal; }

/* -------------------------------------------------- CUSTOM FONTS */
@font-face {
  font-family: Rubik;
  src: local("Rubik-Regular"), url("_Rubik-Regular.woff2") format("woff2");
  font-style: normal;
  font-weight: normal;
  font-display: swap;
}
@font-face {
  font-family: Rubik;
  src: local("Rubik-Bold"), url("_Rubik-Bold.woff2") format("woff2");
  font-style: normal;
  font-weight: bold;
  font-display: swap;
}
@font-face {
  font-family: Rubik;
  src: local("Rubik-Italic"), url("_Rubik-Italic.woff2") format("woff2");
  font-style: italic;
  font-weight: normal;
  font-display: swap;
}
@font-face {
  font-family: Rubik;
  src: local("Rubik-BoldItalic"), url("_Rubik-BoldItalic.woff2") format("woff2");
  font-style: italic;
  font-weight: bold;
  font-display: swap;
}
"""

_DRACULA_CSS = """\
/* Prettify by @pranavdeshai: Dracula — Version 0.1.3 */

/* -------------------------------------------------- PREFERENCES */
:root {
  --card-max-width: 40em;
  --card-text-align: left;
  --font-size-regular: 16px;
  --font-size-small: 14px;
  --font-family: "Source Sans Pro", -apple-system, sytem-ui, BlinkMacSystemFont,
    Segoe UI, Roboto, Helvetica, Arial, sans-serif;
  --img-width: 50%;
  --img-brightness: 1;
  --img-filter: none;
}

/* -------------------------------------------------- COLORS */
.card,
.card.night_mode {
  background-color: #1d1f27;
  --text-fg: #f8f8f2;
  --text-fg-faint: #6272a4;
  --text-bg-selected: #323543;
  --card-bg: #282a36;
  --card-border: #44475a;
  --card-box-shadow: transparent;
  --divider: #6272a4;
  --tag-fg: #282a36;
  --tag-bg: #bd93f9;
  --tag-fg-active: #6272a4;
  --tag-bg-active: #bd93f9;
  --tag-border: transparent;
  --tag-border-active: #bd93f9;
  --cloze-fg: #8be9fd;
  --cloze-bg: transparent;
  --link-fg: #f8f8f2;
  --link-bg: transparent;
  --link-fg-active: #8be9fd;
  --link-bg-active: transparent;
  --bold-fg: #ff79c6;
  --italic-fg: #f1fa8c;
  --bold-italic-fg: #ff5555;
  --underline-fg: #50fa7b;
}

/* -------------------------------------------------- BACKGROUND */
.card {
  cursor: default;
  padding: 0.5em 0;
}
html:not(.mobile) .card {
  padding: 0.5em;
}
.card::-webkit-scrollbar {
  display: none;
}

/* -------------------------------------------------- FLASHCARD */
.prettify-flashcard {
  background-color: var(--card-bg);
  border-radius: 1em;
  border: 1px solid var(--card-border);
  box-shadow: var(--card-box-shadow) 0px 4px 6px;
  color: var(--text-fg);
  font-family: var(--font-family);
  font-size: var(--font-size-regular);
  line-height: 1.5;
  margin: 0 auto;
  max-width: var(--card-max-width);
  text-align: var(--card-text-align);
  word-wrap: break-word;
}
.prettify-flashcard ::selection {
  background-color: var(--text-bg-selected);
}

/* -------------------------------------------------- FIELDS */
.prettify-field {
  margin: 2em;
}
.mobile .prettify-field {
  margin: 1em;
}

.prettify-field--back {
  color: var(--text-fg-faint);
  font-size: var(--font-size-small);
}

/* -------------------------------------------------- CLOZE */
.cloze {
  background-color: var(--cloze-bg);
  color: var(--cloze-fg);
}

/* -------------------------------------------------- DECK */
.prettify-deck {
  margin: 2em;
  display: flex;
  color: var(--text-fg-faint);
  font-size: var(--font-size-small);
  white-space: nowrap;
}
.mobile .prettify-deck {
  margin: 1em;
}

.prettify-subdeck {
  text-decoration: underline;
  text-overflow: ellipsis;
  overflow: hidden;
}

/* -------------------------------------------------- TAGS */
.prettify-tags {
  margin: 2em;
  display: flex;
  flex-flow: row wrap;
  font-size: var(--font-size-small);
}
.mobile .prettify-tags {
  margin: 1em;
}

.prettify-tag {
  all: initial;
  background-color: var(--tag-bg);
  border-radius: 0.25em;
  border: 1px solid var(--tag-border);
  color: var(--tag-fg);
  display: inline;
  font-size: var(--font-size-small);
  font-family: var(--font-family);
  margin: 0 0.5em 0.5em 0;
  padding: 0.25em;
  transition: all 0.25s;
  word-break: break-word;
}
.prettify-tag:hover {
  background-color: var(--tag-bg-active);
  border: 1px solid var(--tag-border-active);
  color: var(--tag-fg-active);
  cursor: pointer;
}

/* -------------------------------------------------- DIVIDER */
.prettify-divider {
  background-color: transparent;
  border: none;
  border-bottom: 1px dashed var(--divider);
  margin: 1em;
  padding: 0;
}

.prettify-divider--answer {
  border-bottom: 1px solid var(--divider);
}

/* -------------------------------------------------- IMAGES */
img {
  border-radius: 0.25em;
  display: block;
  margin: 1em auto;
  max-width: var(--img-width) !important;
}
.night_mode img {
  filter: var(--img-filter);
  opacity: var(--img-brightness);
}
img + br {
  display: none;
}

/* -------------------------------------------------- TABLES */
table {
  border-collapse: separate;
  border-spacing: 0;
  margin: 0 auto;
  max-width: 100%;
}
table thead {
  background-color: var(--text-bg-selected);
}
table tr:nth-of-type(even) {
  background-color: var(--text-bg-selected);
}
table tr:first-child th:first-child { border-top-left-radius: 0.5em; }
table tr:first-child th:last-child  { border-top-right-radius: 0.5em; }
table tr:last-child td:first-child  { border-bottom-left-radius: 0.5em; }
table tr:last-child td:last-child   { border-bottom-right-radius: 0.5em; }
table th {
  border-bottom: solid 1px var(--card-border);
  border-left: solid 1px var(--card-border);
  border-top: solid 1px var(--card-border);
  padding: 0.5em;
}
table th:last-child { border-right: solid 1px var(--card-border); }
table td {
  border-bottom: solid 1px var(--card-border);
  border-left: solid 1px var(--card-border);
  padding: 0.5em;
}
table td:last-of-type { border-right: solid 1px var(--card-border); }

/* -------------------------------------------------- HYPERLINKS */
a, a:visited {
  text-decoration: none;
  color: var(--link-fg-active);
  border-radius: 0.25em;
  padding: 0 0.1em;
  transition: all 0.1s;
}
a:hover, a:active {
  text-decoration: underline;
  color: var(--link-fg-active);
  background-color: var(--link-bg-active);
}

/* -------------------------------------------------- FORMATTING */
b, strong { color: var(--bold-fg); }
i, em     { color: var(--italic-fg); }
b > i, i > b { color: var(--bold-italic-fg); }
u { color: var(--underline-fg); }
pre { white-space: normal; }

/* -------------------------------------------------- CUSTOM FONTS */
@font-face {
  font-family: Source Sans Pro;
  src: local("SourceSansPro-Regular"), url("_SourceSansPro-Regular.woff2") format("woff2");
  font-style: normal;
  font-weight: normal;
  font-display: swap;
}
@font-face {
  font-family: Source Sans Pro;
  src: local("SourceSansPro-Bold"), url("_SourceSansPro-Bold.woff2") format("woff2");
  font-style: normal;
  font-weight: bold;
  font-display: swap;
}
@font-face {
  font-family: Source Sans Pro;
  src: local("SourceSansPro-Italic"), url("_SourceSansPro-Italic.woff2") format("woff2");
  font-style: italic;
  font-weight: normal;
  font-display: swap;
}
@font-face {
  font-family: Source Sans Pro;
  src: local("SourceSansPro-BoldItalic"), url("_SourceSansPro-BoldItalic.woff2") format("woff2");
  font-style: italic;
  font-weight: bold;
  font-display: swap;
}
"""

TEMPLATES = [
    {
        "id": "minimal",
        "name": "Minimal",
        "description": "Clean, modern design with Inter font. Adapts automatically to Anki's light/dark theme.",
        "mode": "both",
        "css": _MINIMAL_CSS,
        "field_colors_light": ["#c47b39", "#2a70a2", "#474747", "#5c7a3e", "#9b6b3a"],
        "field_colors_dark":  ["#eaeaea", "#5da3d5", "#c0c1c1", "#7ec8a0", "#d4a757"],
        "defaults_light": {
            "primary": {"color": "#5c5c5c", "font_size": 16},
            "answer":  {"color": "#5c5c5c", "font_size": 14},
            "extra1":  {"color": "#7875a8", "font_size": 14},
            "extra2":  {"color": "#5f9070", "font_size": 14},
            "audio":   {"color": "#2a70a2", "font_size": 14, "media_width": 280, "media_height": 32},
            "image":   {"color": "#348ccb", "font_size": 14, "media_width": 200, "media_height": 200},
        },
        "defaults_dark": {
            "primary": {"color": "#c0c1c1", "font_size": 16},
            "answer":  {"color": "#c0c1c1", "font_size": 14},
            "extra1":  {"color": "#9e9dc5", "font_size": 14},
            "extra2":  {"color": "#7ab896", "font_size": 14},
            "audio":   {"color": "#2a70a2", "font_size": 14, "media_width": 280, "media_height": 32},
            "image":   {"color": "#348ccb", "font_size": 14, "media_width": 200, "media_height": 200},
        },
    },
    {
        "id": "nord",
        "name": "Nord",
        "description": "Arctic color palette with Rubik font. Adapts automatically to Anki's light/dark theme.",
        "mode": "both",
        "css": _NORD_CSS,
        "field_colors_light": ["#434c5e", "#81a1c1", "#4c566a", "#a3be8c", "#d08770"],
        "field_colors_dark":  ["#e7e9f0", "#81a1c1", "#d8dee9", "#a3be8c", "#ebcb8b"],
        "defaults_light": {
            "primary": {"color": "#4c566a", "font_size": 16},
            "answer":  {"color": "#4c566a", "font_size": 14},
            "extra1":  {"color": "#bf616a", "font_size": 14},
            "extra2":  {"color": "#ebcb8b", "font_size": 14},
            "audio":   {"color": "#81a1c1", "font_size": 14, "media_width": 280, "media_height": 32},
            "image":   {"color": "#88c0d0", "font_size": 14, "media_width": 200, "media_height": 200},
        },
        "defaults_dark": {
            "primary": {"color": "#d8dee9", "font_size": 16},
            "answer":  {"color": "#d8dee9", "font_size": 14},
            "extra1":  {"color": "#bf616a", "font_size": 14},
            "extra2":  {"color": "#ebcb8b", "font_size": 14},
            "audio":   {"color": "#81a1c1", "font_size": 14, "media_width": 280, "media_height": 32},
            "image":   {"color": "#88c0d0", "font_size": 14, "media_width": 200, "media_height": 200},
        },
    },
    {
        "id": "dracula",
        "name": "Dracula",
        "description": "Dark-only theme with vibrant accent colors and Source Sans Pro font.",
        "mode": "dark",
        "css": _DRACULA_CSS,
        "field_colors": ["#ff79c6", "#8be9fd", "#f8f8f2", "#50fa7b", "#f1fa8c"],
        "defaults": {
            "primary": {"color": "#f8f8f2", "font_size": 16},
            "answer":  {"color": "#f8f8f2", "font_size": 14},
            "extra1":  {"color": "#ff79c6", "font_size": 14},
            "extra2":  {"color": "#f1fa8c", "font_size": 14},
            "audio":   {"color": "#f8f8f2", "font_size": 14, "media_width": 280, "media_height": 32},
            "image":   {"color": "#8be9fd", "font_size": 14, "media_width": 200, "media_height": 200},
        },
    },
]
