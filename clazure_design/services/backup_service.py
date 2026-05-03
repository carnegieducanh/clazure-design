from __future__ import annotations

import time
from aqt import mw
from ..config import ADDON_MODULE


MAX_BACKUPS = 5


def _cfg() -> dict:
    cfg = mw.addonManager.getConfig(ADDON_MODULE)
    return cfg if cfg else {"auto_backup": True, "backups": []}


def _save_cfg(cfg: dict) -> None:
    mw.addonManager.writeConfig(ADDON_MODULE, cfg)


def create_backup(model: dict, tmpl: dict) -> dict:
    cfg = _cfg()
    backup = {
        "id": str(int(time.time() * 1000)),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "model_name": model["name"],
        "tmpl_name": tmpl["name"],
        "qfmt": tmpl["qfmt"],
        "afmt": tmpl["afmt"],
        "css": model.get("css", ""),
    }
    backups = cfg.get("backups", [])
    backups.append(backup)
    cfg["backups"] = backups[-MAX_BACKUPS:]
    _save_cfg(cfg)
    return backup


def get_all_backups() -> list[dict]:
    cfg = _cfg()
    backups = cfg.get("backups", [])
    if len(backups) > MAX_BACKUPS:
        backups = backups[-MAX_BACKUPS:]
        cfg["backups"] = backups
        _save_cfg(cfg)
    return list(reversed(backups))


def restore_backup(backup_id: str) -> tuple[bool, str | None]:
    from .anki_service import find_model_by_name, save_model

    backup = next((b for b in _cfg().get("backups", []) if b["id"] == backup_id), None)
    if not backup:
        return False, "Backup not found."

    model = find_model_by_name(backup["model_name"])
    if not model:
        return False, f"Note type '{backup['model_name']}' no longer exists."

    tmpl = next((t for t in model["tmpls"] if t["name"] == backup["tmpl_name"]), None)
    if not tmpl:
        return False, f"Card template '{backup['tmpl_name']}' no longer exists."

    tmpl["qfmt"] = backup["qfmt"]
    tmpl["afmt"] = backup["afmt"]
    model["css"] = backup["css"]
    save_model(model)
    return True, None
