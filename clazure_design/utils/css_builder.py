from .field_utils import sanitize_css_class, is_audio_field, is_image_field

_INPUT_BOX_CSS = """\
/* =========================================
   INPUT BOX
   ========================================= */
.prettify-box { margin: 6px 0; text-align: center; }

.prettify-box input[type=text] {
  min-width: 300px;
  height: 48px;
  padding: 0 10px;
  box-sizing: border-box;
  border-radius: 10px;
  border: 0.5px solid #C4B898;
  font-size: 22px;
  outline: none;
  background-color: #EDE3CC;
  color: #2E1A0A;
  text-align: center;
}

.nightMode .prettify-box input[type=text] {
  color: #C8BEA0;
  background: #211E14;
  border-color: #2E2A1E;
  box-shadow: inset -2px -2px 2px #1E1C14, inset 2px 2px 2px #0E0C08;
}"""

HR_PRESETS = {
    "thin":      {"thickness": 1, "style": "solid",  "color_token": "border", "width_pct": 100, "margin_top": 12, "margin_bottom": 12},
    "fade":      {"thickness": 2, "style": "solid",  "color_token": "muted",  "width_pct": 80,  "margin_top": 12, "margin_bottom": 12, "gradient": True},
    "dashed":    {"thickness": 1, "style": "dashed", "color_token": "muted",  "width_pct": 60,  "margin_top": 12, "margin_bottom": 12},
    "thick":     {"thickness": 3, "style": "solid",  "color_token": "accent", "width_pct": 100, "margin_top": 12, "margin_bottom": 12},
    "invisible": {},
}

_HR_TOKEN_TO_VAR = {
    "border": "var(--divider)",
    "muted":  "var(--text-fg-faint)",
    "accent": "var(--cloze-fg)",
    "text":   "var(--text-fg)",
}


def build_hr_css(hr_style: dict | None) -> str:
    if not hr_style:
        return ""
    preset = hr_style.get("preset", "default")
    if preset == "default":
        return ""
    if preset == "invisible":
        return ".prettify-divider--answer { display: none !important; }"

    cfg = hr_style if preset == "custom" else HR_PRESETS.get(preset)
    if not cfg:
        return ""

    thickness    = cfg.get("thickness", 1)
    style        = cfg.get("style", "solid")
    color_token  = cfg.get("color_token", "border")
    width_pct    = cfg.get("width_pct", 100)
    margin_top   = cfg.get("margin_top", 12)
    margin_bottom = cfg.get("margin_bottom", 12)
    gradient     = cfg.get("gradient", False)

    color_var = _HR_TOKEN_TO_VAR.get(color_token, "var(--divider)")
    rules = ["border: none !important;"]

    if gradient:
        rules.append(f"height: {thickness}px !important;")
        rules.append(f"background: linear-gradient(to right, transparent, {color_var}, transparent) !important;")
    else:
        rules.append(f"border-top: {thickness}px {style} {color_var} !important;")

    if width_pct < 100:
        rules.extend([f"width: {width_pct}% !important;", "margin-left: auto !important;", "margin-right: auto !important;"])
    else:
        rules.append("width: 100% !important;")

    rules.append(f"margin-top: {margin_top}px !important;")
    rules.append(f"margin-bottom: {margin_bottom}px !important;")
    return f".prettify-divider--answer {{ {' '.join(rules)} }}"


def _enc(hex_color: str) -> str:
    return "%23" + hex_color.lstrip("#")


def _svg_headphones(c: str) -> str:
    return (
        f"url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E"
        f"%3Cpath fill='{c}' d='M12 3C7.03 3 3 7.03 3 12v5a2 2 0 0 0 2 2h1"
        f"a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H5v-2c0-3.87 3.13-7 7-7s7 3.13 7 7v2h-1"
        f"a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-5c0-4.97-4.03-9-9-9z'/%3E"
        f"%3C/svg%3E\") center/contain no-repeat"
    )



def build_css(template: dict, front_fields: list, back_fields: list,
              line_height: float | None = None,
              field_gap: int | None = None,
              content_padding: int | None = None,
              card_bg_light: str | None = None,
              card_bg_dark: str | None = None,
              hr_style: dict | None = None,
              compare_field_dicts: list | None = None) -> str:
    base = template.get("css", "")
    overrides = []
    valid_align = {"left", "center", "right"}

    if line_height is not None:
        overrides.append(f".prettify-flashcard {{ line-height: {line_height:.1f} !important; }}")

    if field_gap is not None:
        overrides.append(f".prettify-field {{ margin-top: {field_gap}px !important; margin-bottom: {field_gap}px !important; }}")
        overrides.append(f".prettify-audio-group {{ margin-top: {field_gap}px !important; margin-bottom: {field_gap}px !important; }}")
        overrides.append(f".prettify-audio-group > .prettify-field--audio {{ margin-top: 0 !important; margin-bottom: 0 !important; }}")

    if content_padding:
        overrides.append(
            f".prettify-field:not(.prettify-field--audio):not(.prettify-field--image) "
            f"{{ margin-left: min({content_padding}px, calc(50% - 75px)) !important;"
            f" margin-right: min({content_padding}px, calc(50% - 75px)) !important; }}"
        )

    if card_bg_light:
        overrides.append(f".card:not(.night_mode) .prettify-flashcard {{ background: {card_bg_light} !important; }}")
    if card_bg_dark:
        overrides.append(f".card.night_mode .prettify-flashcard {{ background: {card_bg_dark} !important; }}")

    for f in front_fields + back_fields + (compare_field_dicts or []):
        if f.get("virtual"):
            continue
        slug = sanitize_css_class(f["name"])
        is_media = is_audio_field(f["name"]) or is_image_field(f["name"])
        rules = []
        if f.get("color") and not is_media:
            rules.append(f"color: {f['color']} !important;")
        if f.get("font_size") and not is_media:
            rules.append(f"font-size: {f['font_size']}px !important;")
        font_family = f.get("font_family")
        if isinstance(font_family, str) and font_family.strip() and not is_media:
            safe_family = font_family.strip().replace("'", "\\'")
            rules.append(f"font-family: '{safe_family}' !important;")
        font_weight = f.get("font_weight")
        if isinstance(font_weight, int) and 1 <= font_weight <= 1000 and not is_media:
            rules.append(f"font-weight: {font_weight} !important;")
        font_italic = f.get("font_italic")
        if isinstance(font_italic, bool) and not is_media:
            rules.append(f"font-style: {'italic' if font_italic else 'normal'} !important;")
        align = f.get("align")
        if align in valid_align:
            rules.append(f"text-align: {align} !important;")
            if is_audio_field(f["name"]):
                jc = {"left": "flex-start", "center": "center", "right": "flex-end"}[align]
                rules.append(f"justify-content: {jc} !important;")
        padding_v = f.get("padding_v", 0)
        padding_h = f.get("padding_h", 0)
        if padding_v or padding_h:
            rules.append(f"padding: {padding_v}px {padding_h}px !important;")
        margin_top = f.get("margin_top", 0)
        if margin_top:
            rules.append(f"margin-top: {margin_top}px !important;")
        margin_bottom = f.get("margin_bottom", 0)
        if margin_bottom:
            rules.append(f"margin-bottom: {margin_bottom}px !important;")
        field_lh = f.get("line_height", 0.0)
        if not is_media and isinstance(field_lh, (int, float)) and field_lh > 0:
            rules.append(f"line-height: {field_lh:.1f} !important;")
        if rules:
            overrides.append(f".prettify-f-{slug} {{ {' '.join(rules)} }}")
        if is_image_field(f["name"]):
            width = f.get("media_width", 200)
            height = f.get("media_height", 200)
            if isinstance(width, int) and isinstance(height, int):
                overrides.append(
                    f".prettify-f-{slug} img, .prettify-f-{slug} .img "
                    f"{{ width: {width}px !important; max-width: 100% !important; height: auto !important; max-height: {height}px !important; }}"
                )
        if is_audio_field(f["name"]):
            if f.get("audio_hidden"):
                overrides.append(f".prettify-f-{slug} {{ display: none !important; }}")
                continue
            icon_size = f.get("audio_icon_size")
            if isinstance(icon_size, int):
                player_sel = (
                    f".prettify-f-{slug} .replay-button, "
                    f".prettify-f-{slug} .soundLink, "
                    f".prettify-f-{slug} anki-play"
                )
                before_sel = (
                    f".prettify-f-{slug} .replay-button::before, "
                    f".prettify-f-{slug} .soundLink::before, "
                    f".prettify-f-{slug} anki-play::before"
                )
                overrides.append(
                    f"{player_sel} {{ width: {icon_size}px !important; height: {icon_size}px !important; }}"
                )
                overrides.append(
                    f"{before_sel} {{ width: {icon_size}px !important; height: {icon_size}px !important; }}"
                )
                overrides.append(
                    f".prettify-f-{slug} .prettify-audio-mock "
                    f"{{ width: {icon_size}px !important; height: {icon_size}px !important; }}"
                )
            icon_color = f.get("audio_icon_color")
            if icon_color:
                ec = _enc(icon_color)
                before_sel = (
                    f".prettify-f-{slug} .replay-button::before, "
                    f".prettify-f-{slug} .soundLink::before, "
                    f".prettify-f-{slug} anki-play::before"
                )
                overrides.append(
                    f"{before_sel} {{ background: {_svg_headphones(ec)} !important; }}"
                )
                overrides.append(
                    f".prettify-f-{slug} .prettify-audio-mock {{ color: {icon_color} !important; }}"
                )

    all_audio = [f for f in front_fields + back_fields if not f.get("virtual") and is_audio_field(f["name"])]
    if len(all_audio) >= 2:
        group_align = next((f.get("align") for f in all_audio if f.get("align") in valid_align), None)
        if group_align:
            jc = {"left": "flex-start", "center": "center", "right": "flex-end"}[group_align]
            overrides.append(f".prettify-audio-group {{ justify-content: {jc} !important; }}")

    media_overrides = """
/* media field defaults */
.prettify-field--image img,
.prettify-field--image .img {
  max-width: 100%;
  border-radius: 12px;
  border: solid 1px #c49b63;
  object-fit: cover;
  margin-top: 5px;
  margin-bottom: 5px;
  box-shadow: 0 0 6px gray;
  display: inline-block;
}

.nightMode .prettify-field--image .img,
.nightMode .prettify-field--image img,
.night_mode .prettify-field--image .img,
.night_mode .prettify-field--image img {
  border-color: #2e2a1e;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
}

.prettify-audio-group {
  display: flex;
  flex-direction: row;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.prettify-audio-group > .prettify-field--audio {
  flex: 0 0 auto;
  margin-top: 0;
  margin-bottom: 0;
}

.prettify-field--audio {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.prettify-field--audio audio {
  display: none;
}

/* Preview mock (dialog only) */
.prettify-audio-mock {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  color: #1a1a1a;
}

.nightMode .prettify-audio-mock,
.night_mode .prettify-audio-mock {
  color: #e8eaf0;
}

/* Hide Anki's default play icon */
.prettify-field--audio .replay-button > svg,
.prettify-field--audio .soundLink > svg,
.prettify-field--audio anki-play > svg,
.prettify-field--audio anki-play > button {
  display: none !important;
}
.prettify-field--audio anki-play::part(button) {
  display: none !important;
}

.prettify-field--audio .replay-button,
.prettify-field--audio .soundLink,
.prettify-field--audio anki-play {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
  padding: 0;
  text-decoration: none !important;
  cursor: pointer;
  width: 26px;
  height: 26px;
  transition: transform 0.2s ease, filter 0.2s ease;
}

.prettify-field--audio .replay-button::before,
.prettify-field--audio .soundLink::before,
.prettify-field--audio anki-play::before {
  content: '';
  display: block;
  width: 26px;
  height: 26px;
  flex-shrink: 0;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%231a1a1a' d='M12 3C7.03 3 3 7.03 3 12v5a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H5v-2c0-3.87 3.13-7 7-7s7 3.13 7 7v2h-1a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-5c0-4.97-4.03-9-9-9z'/%3E%3C/svg%3E") center/contain no-repeat;
}

.prettify-field--audio .replay-button::after,
.prettify-field--audio .soundLink::after,
.prettify-field--audio anki-play::after {
  display: none !important;
}

.prettify-field--audio .replay-button:hover,
.prettify-field--audio .soundLink:hover,
.prettify-field--audio anki-play:hover {
  transform: translateY(-3px);
  filter: drop-shadow(0 4px 6px rgba(0,0,0,0.3));
}

/* Dark mode */
.nightMode .prettify-field--audio .replay-button::before,
.nightMode .prettify-field--audio .soundLink::before,
.nightMode .prettify-field--audio anki-play::before,
.night_mode .prettify-field--audio .replay-button::before,
.night_mode .prettify-field--audio .soundLink::before,
.night_mode .prettify-field--audio anki-play::before {
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%23e8eaf0' d='M12 3C7.03 3 3 7.03 3 12v5a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H5v-2c0-3.87 3.13-7 7-7s7 3.13 7 7v2h-1a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-5c0-4.97-4.03-9-9-9z'/%3E%3C/svg%3E") center/contain no-repeat;
}
""".strip()

    hr_css = build_hr_css(hr_style)

    if overrides:
        result = base + "\n/* user overrides */\n" + "\n".join(overrides) + "\n" + media_overrides
    else:
        result = base + "\n" + media_overrides

    if hr_css:
        result += "\n" + hr_css
    result += "\n" + _INPUT_BOX_CSS
    return result
