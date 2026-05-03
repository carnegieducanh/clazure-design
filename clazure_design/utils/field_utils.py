import re
import unicodedata

_ANKI_SPECIAL_TAGS = frozenset({
    "FrontSide", "Tags", "Type", "Deck", "Subdeck", "Card",
    "CardFlag", "Hint", "Edit", "More",
})
_TAG_PREFIX_RE = re.compile(r'^[#^/]|^cloze:|^type:', re.IGNORECASE)


def parse_template_fields(template_html: str, known_fields: set[str]) -> list[str]:
    """Return field names found in an Anki template, in order of first appearance.

    Only returns names that exist in known_fields, skipping Anki special tags.
    """
    seen: set[str] = set()
    result: list[str] = []
    for m in re.finditer(r'\{\{([^}]+)\}\}', template_html):
        raw = m.group(1).strip()
        name = _TAG_PREFIX_RE.sub('', raw).strip()
        if name and name not in _ANKI_SPECIAL_TAGS and name in known_fields and name not in seen:
            seen.add(name)
            result.append(name)
    return result


def sanitize_css_class(field_name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", field_name)
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_only).strip("-").lower()
    return slug or "field"


def normalize_field_name(field_name: str) -> str:
    nfkd = unicodedata.normalize("NFKD", field_name or "")
    ascii_only = nfkd.encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", " ", ascii_only.lower()).strip()


def is_audio_field(field_name: str) -> bool:
    norm = normalize_field_name(field_name)
    return "audio" in norm or "sound" in norm


def is_image_field(field_name: str) -> bool:
    norm = normalize_field_name(field_name)
    return "image" in norm or "img" in norm
