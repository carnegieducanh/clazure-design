"""
Generate Anki-compatible HTML for front/back templates.

front_fields / back_fields: list of {"name": str, "color": str, "font_size": int}
Each field gets class="prettify-field prettify-f-{slug}" for per-field CSS targeting.
"""

from .field_utils import sanitize_css_class, is_audio_field, is_image_field

_HEADPHONES_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" style="flex-shrink:0">'
    '<path fill="currentColor" d="M12 3C7.03 3 3 7.03 3 12v5a2 2 0 0 0 2 2h1'
    'a2 2 0 0 0 2-2v-3a2 2 0 0 0-2-2H5v-2c0-3.87 3.13-7 7-7s7 3.13 7 7v2h-1'
    'a2 2 0 0 0-2 2v3a2 2 0 0 0 2 2h1a2 2 0 0 0 2-2v-5c0-4.97-4.03-9-9-9z"/>'
    '</svg>'
)

_WAVEFORM_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 52 20" width="52" height="20" style="flex-shrink:0">'
    '<rect fill="currentColor" x="0" y="8" width="3" height="4" rx="1"/>'
    '<rect fill="currentColor" x="6" y="4" width="3" height="12" rx="1"/>'
    '<rect fill="currentColor" x="12" y="1" width="3" height="18" rx="1"/>'
    '<rect fill="currentColor" x="18" y="4" width="3" height="12" rx="1"/>'
    '<rect fill="currentColor" x="24" y="7" width="3" height="6" rx="1"/>'
    '<rect fill="currentColor" x="30" y="3" width="3" height="14" rx="1"/>'
    '<rect fill="currentColor" x="36" y="0" width="3" height="20" rx="1"/>'
    '<rect fill="currentColor" x="42" y="5" width="3" height="10" rx="1"/>'
    '<rect fill="currentColor" x="48" y="8" width="3" height="4" rx="1"/>'
    '</svg>'
)


_TYPE_ANSWER_BOX = "__type_answer_box__"

_TYPE_ANSWER_HTML = (
    '<div class="prettify-box">\n'
    '  <input id="type-word" type="text" placeholder="Type your word here... ✍️">\n'
    '  <div id="answer-feedback" style="margin: 10px; font-size: 20px;"></div>\n'
    '</div>'
)


def _type_answer_scripts(compare_field: str) -> str:
    cf = compare_field
    return (
        "<script>\n"
        "document.getElementById('type-word').addEventListener('input', function() {\n"
        "  var userAnswer = this.value.trim().toLowerCase();\n"
        f'  var correctAnswer = "{{{{{cf}}}}}".trim().toLowerCase();\n'
        '  var resultHTML = "";\n'
        "  var maxLength = Math.max(userAnswer.length, correctAnswer.length);\n"
        "  for (var i = 0; i < maxLength; i++) {\n"
        "    if (userAnswer[i] === correctAnswer[i]) {\n"
        '      resultHTML += \'<span style="color:#ff557f;font-weight:bold;">\' + (userAnswer[i] || \'\') + \'</span>\';\n'
        "    } else {\n"
        '      resultHTML += \'<span style="color:#FFDD3B;">\' + (userAnswer[i] || \'_\') + \'</span>\';\n'
        "    }\n"
        "  }\n"
        "  document.getElementById('answer-feedback').innerHTML = resultHTML;\n"
        "});\n"
        "</script>\n\n"
        "<script>\n"
        "document.getElementById('type-word').addEventListener('keydown', function(e) {\n"
        "  if (e.key === 'Enter') {\n"
        "    e.preventDefault();\n"
        '    if (typeof pycmd !== "undefined") pycmd("ans");\n'
        "  }\n"
        "});\n"
        "</script>\n\n"
        "<script>\n"
        "(function focusInput() {\n"
        '  var input = document.getElementById("type-word");\n'
        "  if (input) { input.focus(); }\n"
        "  else { setTimeout(focusInput, 100); }\n"
        "})();\n"
        "</script>"
    )


def _ref(field: str) -> str:
    return "{{" + field + "}}"


def _cond(field: str, inner: str) -> str:
    return "{{#" + field + "}}" + inner + "{{/" + field + "}}"


def _cond_formatted(field: str, inner: str, indent: str = "  ") -> str:
    return f"{{{{#{field}}}}}\n{indent}{inner}\n{{{{/{field}}}}}"


def _field_div(field: dict, back: bool = False) -> str:
    slug = sanitize_css_class(field["name"])
    classes = f"prettify-field prettify-f-{slug}"
    if is_audio_field(field["name"]):
        classes += " prettify-field--audio"
    if is_image_field(field["name"]):
        classes += " prettify-field--image"
    if back:
        classes += " prettify-field--back"
    return classes  # caller inserts content


def _preview_content(field_name: str) -> str:
    if is_audio_field(field_name):
        return (
            f'<div class="prettify-audio-mock">'
            f'{_HEADPHONES_SVG}'
            f'{_WAVEFORM_SVG}'
            f'</div>'
        )
    if is_image_field(field_name):
        return (
            "<img alt='preview image' "
            "src=\"data:image/svg+xml;utf8,"
            "<svg xmlns='http://www.w3.org/2000/svg' width='240' height='240' viewBox='0 0 240 240'>"
            "<rect width='240' height='240' fill='%23f0e6d8'/>"
            "<circle cx='82' cy='84' r='24' fill='%23c49b63'/>"
            "<path d='M30 190 L95 120 L138 156 L178 110 L210 190 Z' fill='%23c49b63'/>"
            "<text x='120' y='222' text-anchor='middle' font-size='14' fill='%23705c3c'>Image preview</text>"
            "</svg>\"/>"
        )
    return f"[{field_name}]"


def _field_rows(fields: list, back: bool, preview: bool, empty_msg: str, replace_virtual: bool = False) -> tuple[list, str]:
    if not fields:
        return [
            f'<p style="color:#999;font-size:13px;text-align:center;padding:2em">{empty_msg}</p>'
        ], ""
    rows = []
    scripts = ""
    for f in fields:
        if f.get("virtual"):
            cf = f.get("compare_field", "")
            if replace_virtual:
                if cf:
                    content = _preview_content(cf) if preview else _ref(cf)
                    inner = f'<div class="{_field_div({"name": cf}, back=back)}">{content}</div>'
                    if preview:
                        rows.append(inner)
                    else:
                        rows.append(_cond_formatted(cf, inner))
            else:
                rows.append(_TYPE_ANSWER_HTML)
                if not preview and cf:
                    scripts = _type_answer_scripts(cf)
        else:
            content = _preview_content(f["name"]) if preview else _ref(f["name"])
            inner = f'<div class="{_field_div(f, back=back)}">{content}</div>'
            if preview:
                rows.append(inner)
            else:
                rows.append(_cond_formatted(f["name"], inner))
    return rows, scripts


def build_front(front_fields: list, preview: bool = False) -> str:
    rows, scripts = _field_rows(
        front_fields, back=False, preview=preview,
        empty_msg="Add fields to Front to see content"
    )
    if preview:
        parts = ['<div class="prettify-flashcard">'] + rows + ["</div>"]
        if scripts:
            parts.append(scripts)
        return "\n".join(parts)
    else:
        content = "\n\n".join(rows)
        result = f'<div class="prettify-flashcard">\n{content}\n</div>'
        if scripts:
            result += "\n" + scripts
        return result


def build_back(front_fields: list, back_fields: list, preview: bool = False) -> str:
    divider = '<hr id="answer" class="prettify-divider prettify-divider--answer">'
    front_names = {f["name"] for f in front_fields if not f.get("virtual")}
    unique_back = [f for f in back_fields if f.get("virtual") or f["name"] not in front_names]
    front_rows, front_scripts = _field_rows(
        front_fields, back=False, preview=preview,
        empty_msg="Add fields to Front to see content",
        replace_virtual=True,
    )
    back_rows, back_scripts = _field_rows(
        unique_back, back=True, preview=preview,
        empty_msg="Add fields to Back to see content"
    )
    scripts = front_scripts or back_scripts
    if preview:
        parts = (
            ['<div class="prettify-flashcard">']
            + front_rows
            + [divider]
            + back_rows
            + ["</div>"]
        )
        if scripts:
            parts.append(scripts)
        return "\n".join(parts)
    else:
        front_content = "\n\n".join(front_rows)
        back_content = "\n\n".join(back_rows)
        result = f'<div class="prettify-flashcard">\n{front_content}\n\n{divider}\n\n{back_content}\n</div>'
        if scripts:
            result += "\n" + scripts
        return result
