from aqt import mw, gui_hooks
from aqt.qt import QAction, QMenu

from . import bg  # registers CSS injection hooks


def _current_card_info() -> tuple[str | None, int]:
    try:
        card = mw.reviewer.card
        if card:
            return card.note_type()["name"], card.ord
    except Exception:
        pass
    return None, 0


def _open_card_design():
    from .ui.dialog import PrettifyDialog
    note_type, card_ord = _current_card_info()
    dlg = PrettifyDialog(mw, initial_note_type=note_type, initial_card_tmpl_ord=card_ord)
    dlg.exec()


def _open_bg():
    from .bg.gui_updatemanager import SettingsDialogExecute
    SettingsDialogExecute()


def _setup_menu():
    menu = QMenu("Clazure Design", mw)
    card_action = QAction("Card Design", mw)
    card_action.triggered.connect(_open_card_design)
    menu.addAction(card_action)
    bg_action = QAction("Background", mw)
    bg_action.triggered.connect(_open_bg)
    menu.addAction(bg_action)
    mw.menuBar().addMenu(menu)


gui_hooks.main_window_did_init.append(_setup_menu)
