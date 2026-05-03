from __future__ import annotations

from aqt import mw


def get_note_types():
    """Return all note type models sorted by name."""
    return sorted(mw.col.models.all(), key=lambda m: m["name"].lower())


def get_fields(model: dict) -> list[str]:
    return [f["name"] for f in model["flds"]]


def get_card_templates(model: dict) -> list[dict]:
    return model["tmpls"]


def find_model_by_name(name: str) -> dict | None:
    return mw.col.models.by_name(name)


def save_model(model: dict) -> None:
    """Save model, compatible with Anki 2.1.45+ and older."""
    try:
        mw.col.models.update_dict(model)   # Anki 2.1.45+
    except AttributeError:
        mw.col.models.save(model)
    mw.reset()


def apply_template(model: dict, tmpl_ord: int, front: str, back: str, css: str) -> None:
    for tmpl in model["tmpls"]:
        if tmpl["ord"] == tmpl_ord:
            tmpl["qfmt"] = front
            tmpl["afmt"] = back
            break
    model["css"] = css
    save_model(model)
