from __future__ import annotations
import json

from aqt.qt import (
    QDialog, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QComboBox, QGroupBox, QTabWidget,
    QScrollArea, QWidget, QMessageBox, QSpinBox, QDoubleSpinBox, QAbstractSpinBox,
    QDialogButtonBox, QListWidget, QListWidgetItem,
    Qt, QColor, QColorDialog, QSizePolicy, QFrame, QFontDialog, QFont,
    QPainter, QPoint, QPen, QMimeData, QDrag, QSplitter,
    QApplication, QTimer, QPixmap, QCursor, QObject, QEvent,
    QSlider, QCheckBox, QBrush, QLinearGradient,
    QGridLayout, QGraphicsOpacityEffect,
)
from aqt import mw

from ..services.anki_service import (
    get_note_types, get_fields, get_card_templates, save_model,
)
from ..services.backup_service import create_backup, get_all_backups, restore_backup
from ..config import ADDON_MODULE
from ..templates.registry import get_all as get_all_templates
from ..utils.html_builder import build_front, build_back
from ..utils.css_builder import build_css, HR_PRESETS
from ..utils.field_utils import sanitize_css_class, is_audio_field, is_image_field, normalize_field_name, parse_template_fields

FIELD_MIME = "application/x-prettify-field"
_TYPE_ANSWER_BOX = "__type_answer_box__"

UI_BG_MAIN = "#eef2f7"
UI_BG_PANEL = "#f6f8fc"
UI_BG_CARD = "#fbfcff"
UI_BG_LIST = "#f3f6fb"
UI_BG_ROW = "#f7f9fd"
UI_BG_ROW_HOVER = "#e9f0fb"
UI_BG_HOVER = "#eef3fb"
UI_BORDER = "#cfd8e6"
UI_BORDER_STRONG = "#b8c5d9"
UI_TEXT = "#2f3b4f"
UI_TEXT_MUTED = "#5f6e84"
UI_ACCENT = "#2f7fd8"


def _is_night_mode() -> bool:
    try:
        from aqt.theme import theme_manager
        return theme_manager.night_mode
    except Exception:
        try:
            return bool(mw.pm.night_mode())
        except Exception:
            return False


def _apply_theme(dark: bool) -> None:
    global UI_BG_MAIN, UI_BG_PANEL, UI_BG_CARD, UI_BG_LIST
    global UI_BG_ROW, UI_BG_ROW_HOVER, UI_BG_HOVER, UI_BORDER, UI_BORDER_STRONG
    global UI_TEXT, UI_TEXT_MUTED, UI_ACCENT
    if dark:
        UI_BG_MAIN       = "#1e1e1e"
        UI_BG_PANEL      = "#252525"
        UI_BG_CARD       = "#2e2e2e"
        UI_BG_LIST       = "#1a1a1a"
        UI_BG_ROW        = "#2a2a2a"
        UI_BG_ROW_HOVER  = "#353535"
        UI_BG_HOVER      = "#3a3a3a"
        UI_BORDER        = "#404040"
        UI_BORDER_STRONG = "#5c5c5c"
        UI_TEXT          = "#e8e8e8"
        UI_TEXT_MUTED    = "#a0a0a0"
        UI_ACCENT        = "#0078d4"
    else:
        UI_BG_MAIN       = "#eef2f7"
        UI_BG_PANEL      = "#f6f8fc"
        UI_BG_CARD       = "#fbfcff"
        UI_BG_LIST       = "#f3f6fb"
        UI_BG_ROW        = "#f7f9fd"
        UI_BG_ROW_HOVER  = "#e9f0fb"
        UI_BG_HOVER      = "#eef3fb"
        UI_BORDER        = "#cfd8e6"
        UI_BORDER_STRONG = "#b8c5d9"
        UI_TEXT          = "#2f3b4f"
        UI_TEXT_MUTED    = "#5f6e84"
        UI_ACCENT        = "#2f7fd8"


def _is_light(hex_color: str) -> bool:
    c = QColor(hex_color)
    return (c.red() * 299 + c.green() * 587 + c.blue() * 114) / 1000 > 180


def _hex_to_rgba(hex_color: str, opacity: float) -> str:
    c = QColor(hex_color)
    return f"rgba({c.red()},{c.green()},{c.blue()},{opacity:.2f})"


def _position_before_preview(dlg: QDialog, requester: QWidget, gap: int = 16) -> None:
    """Move dlg so its right edge sits gap px to the left of the preview panel."""
    dlg.adjustSize()
    w = requester
    while w is not None:
        if hasattr(w, "preview_tabs"):
            break
        w = w.parent()
    if w is None:
        return
    preview_global = w.preview_tabs.mapToGlobal(QPoint(0, 0))
    dlg_w = dlg.sizeHint().width()
    dlg_h = dlg.sizeHint().height()
    x = preview_global.x() - gap - dlg_w
    main_top = w.mapToGlobal(QPoint(0, 0)).y()
    y = main_top + (w.height() - dlg_h) // 2
    screen = QApplication.primaryScreen().availableGeometry()
    x = max(screen.left(), min(x, screen.right() - dlg_w))
    y = max(screen.top(), min(y, screen.bottom() - dlg_h))
    dlg.move(x, y)


def _make_eyedropper_cursor() -> QCursor:
    try:
        from PyQt6.QtSvg import QSvgRenderer
        from PyQt6.QtCore import QByteArray
        # 20×20 output; viewBox 24×24 → hotspot: (3/24)*20≈2, (21/24)*20≈17
        svg = QByteArray(b"""<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='20' height='20'>
  <path fill='none' stroke='#222' stroke-width='3' stroke-linejoin='round' stroke-linecap='round'
    d='M20.71 5.63l-2.34-2.34a1 1 0 0 0-1.41 0l-3.12 3.12-1.41-1.42-1.42 1.42
       1.41 1.41L3 17.25V21h3.75l9.88-9.88 1.41 1.41 1.42-1.42-1.42-1.41
       3.12-3.12a1 1 0 0 0 0-1.41z'/>
  <path fill='white'
    d='M20.71 5.63l-2.34-2.34a1 1 0 0 0-1.41 0l-3.12 3.12-1.41-1.42-1.42 1.42
       1.41 1.41L3 17.25V21h3.75l9.88-9.88 1.41 1.41 1.42-1.42-1.42-1.41
       3.12-3.12a1 1 0 0 0 0-1.41z'/>
</svg>""")
        renderer = QSvgRenderer(svg)
        px = QPixmap(20, 20)
        px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        renderer.render(p)
        p.end()
        return QCursor(px, 2, 17)
    except Exception:
        return QCursor(Qt.CursorShape.CrossCursor)


class _EyedropperEnforcer(QObject):
    """Keeps eyedropper cursor active during screen color picking.

    Qt's WM_SETCURSOR handler prioritises the grabMouse cursor (crosshair)
    over the application override cursor, even outside the dialog window.
    We work around this by:
      1. Setting QApplication.setOverrideCursor (covers Qt-managed areas).
      2. Capturing the resulting Win32 HCURSOR via GetCursor().
      3. Calling SetCursor(hcursor) every 8 ms (Win32 direct) so the cursor
         stays consistent everywhere, including other app windows on screen.
    MouseButtonRelease (= end of pick) is detected via an app-level event
    filter to clean everything up.
    """

    def __init__(self, cursor: QCursor, parent=None):
        super().__init__(parent)
        self._cursor = cursor
        self._hcursor = 0
        self._active = False
        self._timer = QTimer(self)
        self._timer.setInterval(8)
        self._timer.timeout.connect(self._enforce)

    def start(self) -> None:
        if self._active:
            return
        self._active = True
        QApplication.setOverrideCursor(self._cursor)
        try:
            import ctypes
            self._hcursor = ctypes.windll.user32.GetCursor()
        except Exception:
            self._hcursor = 0
        self._timer.start()
        QApplication.instance().installEventFilter(self)

    def stop(self) -> None:
        if not self._active:
            return
        self._active = False
        self._timer.stop()
        QApplication.instance().removeEventFilter(self)
        if QApplication.overrideCursor() is not None:
            QApplication.restoreOverrideCursor()

    def _enforce(self) -> None:
        QApplication.changeOverrideCursor(self._cursor)
        if self._hcursor:
            try:
                import ctypes
                ctypes.windll.user32.SetCursor(self._hcursor)
            except Exception:
                pass

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.Type.MouseButtonRelease:
            QTimer.singleShot(0, self.stop)
        return False


# ─── Line Height Spin Box (with manual ▲/▼ buttons) ────────────────────────────

class _SpinArrowBtn(QPushButton):
    """Button that paints a native-style spinbox arrow triangle."""

    def __init__(self, up: bool, top_corner: bool, parent=None):
        super().__init__(parent)
        self._up = up
        self.setFixedSize(12, 11)
        self.setStyleSheet(
            "QPushButton {"
            " border: none; background: transparent;"
            " padding: 0; margin: 0;"
            "}"
            "QPushButton:hover { background: transparent; }"
            "QPushButton:pressed { background: transparent; }"
        )

    def paintEvent(self, event):
        super().paintEvent(event)
        w, h = self.width(), self.height()
        cx, cy = w // 2, h // 2
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QPen(Qt.PenStyle.NoPen))
        p.setBrush(QBrush(QColor(UI_TEXT_MUTED)))
        if self._up:
            pts = [QPoint(cx - 3, cy + 2), QPoint(cx + 3, cy + 2), QPoint(cx, cy - 2)]
        else:
            pts = [QPoint(cx - 3, cy - 2), QPoint(cx + 3, cy - 2), QPoint(cx, cy + 2)]
        p.drawPolygon(pts)
        p.end()


class LineHeightSpinBox(QWidget):
    """Custom spinbox with ▲/▼ buttons stacked on right inside."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(60, 22)
        self.setObjectName("lineHeightSpinBox")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        # Outer container with border-radius
        self.setStyleSheet(
            "#lineHeightSpinBox {"
            f" border: 1px solid {UI_BORDER}; border-radius: 4px;"
            f" background: {UI_BG_CARD}; padding: 0;"
            "}"
        )
        
        hl = QHBoxLayout(self)
        hl.setContentsMargins(0, 0, 0, 0)
        hl.setSpacing(0)
        
        # Spinbox (no buttons, left side)
        self._spin = NoWheelDoubleSpinBox()
        self._spin.setRange(0.5, 2.0)
        self._spin.setSingleStep(0.1)
        self._spin.setValue(1.0)
        self._spin.setDecimals(1)
        self._spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self._spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._spin.setStyleSheet(
            "QDoubleSpinBox {"
            f" font-size: 10px; font-weight: 600; color: {UI_TEXT};"
            " border: none; border-radius: 0;"
            f" background: transparent; padding: 0 8px;"
            "}"
            "QDoubleSpinBox:focus {"
            f" outline: none;"
            "}"
        )
        hl.addWidget(self._spin)
        
        # Vertical stack of up/down buttons (right side, flush to border)
        btn_vbox = QVBoxLayout()
        btn_vbox.setContentsMargins(0, 1, 1, 1)
        btn_vbox.setSpacing(0)

        self._up_btn = _SpinArrowBtn(up=True, top_corner=True)
        self._up_btn.clicked.connect(self._on_up)
        btn_vbox.addWidget(self._up_btn)

        self._down_btn = _SpinArrowBtn(up=False, top_corner=False)
        self._down_btn.clicked.connect(self._on_down)
        btn_vbox.addWidget(self._down_btn)

        btn_container = QWidget()
        btn_container.setLayout(btn_vbox)
        btn_container.setFixedWidth(13)
        btn_container.setAutoFillBackground(False)
        btn_container.setStyleSheet("QWidget { background: transparent; }")
        hl.addWidget(btn_container)
    
    def _on_up(self):
        val = self._spin.value()
        self._spin.setValue(val + self._spin.singleStep())
    
    def _on_down(self):
        val = self._spin.value()
        self._spin.setValue(val - self._spin.singleStep())
    
    def value(self) -> float:
        return self._spin.value()
    
    def setValue(self, val: float):
        self._spin.setValue(val)
    
    def valueChanged(self):
        return self._spin.valueChanged
    
    def connect(self, slot):
        """Connect to valueChanged signal."""
        self._spin.valueChanged.connect(slot)

    def setRange(self, min_val: float, max_val: float):
        self._spin.setRange(min_val, max_val)

    def wheelEvent(self, event):
        event.ignore()


# ─── HR Style helpers ─────────────────────────────────────────────────────────

_HR_PREVIEW_COLORS_LIGHT = {
    "border": QColor("#b0b8c0"),
    "muted":  QColor("#9099a5"),
    "accent": QColor("#5b8dd9"),
    "text":   QColor("#333333"),
}
_HR_PREVIEW_COLORS_DARK = {
    "border": QColor("#484e5c"),
    "muted":  QColor("#6a7488"),
    "accent": QColor("#7aabdf"),
    "text":   QColor("#d0d8e0"),
}


class _HRPreview(QWidget):
    def __init__(self, preset_key: str, dark: bool = False, parent=None):
        super().__init__(parent)
        self._key  = preset_key
        self._dark = dark
        self.setFixedHeight(20)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        colors = _HR_PREVIEW_COLORS_DARK if self._dark else _HR_PREVIEW_COLORS_LIGHT
        w, h   = self.width(), self.height()
        mid    = h // 2

        if self._key == "default":
            p.setPen(QPen(colors["border"], 1, Qt.PenStyle.DashLine))
            p.drawLine(4, mid, w - 4, mid)

        elif self._key == "thin":
            p.setPen(QPen(colors["border"], 1, Qt.PenStyle.SolidLine))
            p.drawLine(4, mid, w - 4, mid)

        elif self._key == "fade":
            c    = QColor(colors["muted"])
            grad = QLinearGradient(4, 0, w - 4, 0)
            t    = QColor(c); t.setAlpha(0)
            grad.setColorAt(0.0, t)
            grad.setColorAt(0.5, c)
            grad.setColorAt(1.0, t)
            p.setPen(Qt.PenStyle.NoPen)
            p.fillRect(4, mid - 1, w - 8, 2, QBrush(grad))

        elif self._key == "dashed":
            x0 = w // 5
            p.setPen(QPen(colors["muted"], 1, Qt.PenStyle.DashLine))
            p.drawLine(x0, mid, w - x0, mid)

        elif self._key == "thick":
            pen = QPen(colors["accent"], 3, Qt.PenStyle.SolidLine)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            p.setPen(pen)
            p.drawLine(6, mid, w - 6, mid)

        elif self._key == "invisible":
            p.setPen(QPen(QColor("#aaaaaa"), 1))
            p.drawText(0, 0, w, h, Qt.AlignmentFlag.AlignCenter, "hidden")

        p.end()


class _PresetCard(QFrame):
    def __init__(self, key: str, label: str, dark: bool, on_select, parent=None):
        super().__init__(parent)
        self._key       = key
        self._on_select = on_select
        self._selected  = False

        self.setFixedSize(104, 64)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        vl = QVBoxLayout(self)
        vl.setContentsMargins(6, 8, 6, 6)
        vl.setSpacing(4)

        preview = _HRPreview(key, dark)
        vl.addWidget(preview)

        name_lbl = QLabel(label)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet(f"font-size: 10px; color: {UI_TEXT}; background: transparent;")
        vl.addWidget(name_lbl)

        self._update_style()

    def set_selected(self, v: bool):
        self._selected = v
        self._update_style()

    def _update_style(self):
        if self._selected:
            self.setStyleSheet(
                f"QFrame {{ background: {UI_BG_CARD}; border: 2px solid {UI_ACCENT}; border-radius: 6px; }}"
            )
        else:
            self.setStyleSheet(
                f"QFrame {{ background: {UI_BG_CARD}; border: 1px solid {UI_BORDER}; border-radius: 6px; }}"
                f"QFrame:hover {{ border-color: {UI_BORDER_STRONG}; }}"
            )

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._on_select(self._key)


# ─── Field Row Widget ─────────────────────────────────────────────────────────

class NoWheelSpinBox(QSpinBox):
    def wheelEvent(self, event):
        event.ignore()


class NoWheelDoubleSpinBox(QDoubleSpinBox):
    def wheelEvent(self, event):
        event.ignore()


class NoWheelComboBox(QComboBox):
    def wheelEvent(self, event):
        event.ignore()


class AlignIconButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._align = "left"
        self.setFlat(True)
        self.setStyleSheet(
            "QPushButton {"
            f" border: 1px solid {UI_BORDER}; border-radius: 4px;"
            f" background: {UI_BG_CARD};"
            "}"
            "QPushButton:hover {"
            f" border-color: {UI_BORDER_STRONG}; background: {UI_BG_HOVER};"
            "}"
        )

    def set_align(self, align: str):
        self._align = align if align in ("left", "center", "right") else "left"
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        pen = QPen(QColor(UI_TEXT))
        pen.setWidth(2)
        pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        p.setPen(pen)
        w = self.width()
        h = self.height()
        ys = [max(4, h // 2 - 5), h // 2, min(h - 4, h // 2 + 5)]
        lens = [w - 12, w - 8, w - 12]
        for y, ln in zip(ys, lens):
            if self._align == "left":
                x1 = 4
            elif self._align == "center":
                x1 = (w - ln) // 2
            else:
                x1 = w - 4 - ln
            x2 = x1 + ln
            p.drawLine(x1, y, x2, y)
        p.end()


class FieldRowWidget(QFrame):
    ROW_H        = 36
    COLOR_W      = 22
    ALIGN_W      = 26
    FONT_W       = 42
    # Wider "Size" column to prevent value text being clipped/covered
    # (e.g., "200x200", "280x32") and to give room for QSpinBox arrows.
    SPIN_W       = 70
    SIZE_BTN_W   = 70
    SPACING_BTN_W = 52

    def __init__(self, field: dict, on_changed=None, parent=None):
        super().__init__(parent)
        self._field      = dict(field)
        self._on_changed = on_changed
        self._drag_start: QPoint | None = None

        self.setFixedHeight(self.ROW_H)
        self.setAttribute(Qt.WidgetAttribute.WA_Hover, True)
        self.setStyleSheet(
            "FieldRowWidget {"
            f" background: {UI_BG_ROW};"
            f" border: 1px solid {UI_BORDER};"
            " border-radius: 6px;"
            "}"
            "FieldRowWidget:hover {"
            f" background: {UI_BG_ROW_HOVER}; border-color: {UI_BORDER_STRONG};"
            "}"
        )

        hl = QHBoxLayout(self)
        hl.setContentsMargins(4, 0, 8, 0)
        hl.setSpacing(6)

        handle = QLabel("⠿")
        handle.setFixedWidth(20)
        handle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        handle.setStyleSheet(f"color: {UI_BORDER_STRONG}; font-size: 15px;")
        handle.setCursor(Qt.CursorShape.OpenHandCursor)
        hl.addWidget(handle)

        self._name_lbl = QLabel(field["name"])
        self._name_lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._name_lbl.setStyleSheet(f"color: {UI_TEXT}; font-size: 12px; font-weight: 500;")
        hl.addWidget(self._name_lbl)

        self._color_btn = QPushButton()
        self._color_btn.setFixedSize(self.COLOR_W, self.COLOR_W)
        self._color_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._color_btn.clicked.connect(self._on_color_clicked)
        self._refresh_color()
        hl.addWidget(self._color_btn)

        self._font_btn = QPushButton("Aa ▾")
        self._font_btn.setFixedSize(self.FONT_W, self.COLOR_W)
        self._font_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._font_btn.setStyleSheet(
            "QPushButton {"
            f" border: 1px solid {UI_BORDER}; border-radius: 4px;"
            f" background: {UI_BG_CARD}; color: {UI_TEXT};"
            " font-size: 10px; font-weight: 700; padding: 0 2px;"
            "}"
            "QPushButton:hover {"
            f" border-color: {UI_BORDER_STRONG}; background: {UI_BG_HOVER};"
            "}"
        )
        self._font_btn.clicked.connect(self._pick_font_family)
        self._refresh_font_button()
        hl.addWidget(self._font_btn)

        self._align_btn = AlignIconButton()
        self._align_btn.setFixedSize(self.ALIGN_W, self.COLOR_W)
        self._align_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._align_btn.clicked.connect(self._cycle_align)
        align = field.get("align", "left")
        if align not in ("left", "center", "right"):
            align = "left"
        self._set_align(align, notify=False)
        hl.addWidget(self._align_btn)

        self._spin = NoWheelSpinBox()
        self._spin.setRange(8, 72)
        self._spin.setValue(field.get("font_size", 16))
        self._spin.setSuffix("px")
        self._spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._spin.setFixedWidth(self.SPIN_W)
        self._spin.setFixedHeight(self.COLOR_W)
        self._spin.setStyleSheet(
            "QSpinBox {"
            f" font-size: 10px; font-weight: 600; color: {UI_TEXT};"
            f" border: 1px solid {UI_BORDER}; border-radius: 4px;"
            # Reduce padding so the value text doesn't get pushed under
            # the built-in up/down buttons.
            f" background: {UI_BG_CARD}; padding: 0 6px 0 6px;"
            "}"
            "QSpinBox:hover {"
            f" border-color: {UI_BORDER_STRONG};"
            "}"
            "QSpinBox:focus {"
            f" border-color: {UI_ACCENT};"
            "}"
            "QSpinBox::up-button {"
            f" background: {UI_BG_CARD}; width: 12px; height: 11px;"
            f" border-left: 1px solid {UI_BORDER}; border-top-right-radius: 4px;"
            " subcontrol-origin: border; subcontrol-position: top right;"
            "}"
            "QSpinBox::down-button {"
            f" background: {UI_BG_CARD}; width: 12px; height: 11px;"
            f" border-left: 1px solid {UI_BORDER}; border-bottom-right-radius: 4px;"
            " subcontrol-origin: border; subcontrol-position: bottom right;"
            "}"
            "QSpinBox::up-button:hover, QSpinBox::down-button:hover {"
            f" background: {UI_BG_HOVER};"
            "}"
            "QSpinBox::up-arrow, QSpinBox::down-arrow {"
            " width: 9px; height: 9px;"
            "}"
        )
        self._spin.valueChanged.connect(self._size_changed)
        hl.addWidget(self._spin)

        self._media_size_btn = QPushButton("Size")
        self._media_size_btn.setFixedSize(self.SIZE_BTN_W, self.COLOR_W)
        self._media_size_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._media_size_btn.setStyleSheet(
            "QPushButton {"
            f" border: 1px solid {UI_BORDER}; border-radius: 4px;"
            f" background: {UI_BG_CARD}; color: {UI_TEXT};"
            " font-size: 10px; font-weight: 600; padding: 0 4px;"
            "}"
            "QPushButton:hover {"
            f" border-color: {UI_BORDER_STRONG}; background: {UI_BG_HOVER};"
            "}"
        )
        self._media_size_btn.clicked.connect(self._edit_media_size)
        hl.addWidget(self._media_size_btn)

        self._spacing_btn = QPushButton("Spacing")
        self._spacing_btn.setFixedSize(self.SPACING_BTN_W, self.COLOR_W)
        self._spacing_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._spacing_btn.clicked.connect(self._edit_spacing)
        hl.addWidget(self._spacing_btn)

        self._refresh_control_mode()
        self._refresh_spacing_button()

        self._interactive_controls = [
            self._color_btn, self._font_btn, self._align_btn,
            self._spin, self._media_size_btn, self._spacing_btn,
        ]
        self._opacity_effect = QGraphicsOpacityEffect(self)
        self._opacity_effect.setOpacity(1.0)
        self.setGraphicsEffect(self._opacity_effect)

        self._compare_chip: QLabel | None = None
        if self._field.get("virtual"):
            self._name_lbl.setText("✍️ Type Answer Box")
            self._compare_chip = QLabel()
            hl.addWidget(self._compare_chip)
            self._refresh_compare_chip()

    # ── Public ─────────────────────────────────────────────────────────────────

    def get_field(self) -> dict:
        return dict(self._field)

    def set_color(self, color: str):
        self._field["color"] = color
        self._refresh_color()

    def set_dimmed(self, dimmed: bool) -> None:
        self._opacity_effect.setOpacity(0.38 if dimmed else 1.0)
        for ctrl in self._interactive_controls:
            ctrl.setEnabled(not dimmed)
        self.setToolTip("Will be shown above divider" if dimmed else "")

    # ── Private ────────────────────────────────────────────────────────────────

    def _refresh_color(self):
        color  = self._field.get("color", "#333333")
        border = "#78889f" if _is_light(color) else "#2f3b4f"
        self._color_btn.setStyleSheet(
            f"QPushButton {{ background-color: {color}; border: 1px solid {border}; border-radius: 4px; }}"
            f"QPushButton:hover {{ border-color: {UI_ACCENT}; }}"
            f"QPushButton:pressed {{ border-color: {UI_TEXT}; }}"
        )
        self._color_btn.setToolTip(f"Text color: {color}")

    def _edit_color(self):
        pre = self._field.get("color", "#333333")
        dlg = QColorDialog(QColor(pre), self)
        dlg.setWindowTitle("Field Text Color")
        dlg.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)

        for box in dlg.findChildren(QDialogButtonBox):
            ok = box.button(QDialogButtonBox.StandardButton.Ok)
            if ok:
                ok.setText("Save")

        _enforcer = _EyedropperEnforcer(_make_eyedropper_cursor(), dlg)
        for btn in dlg.findChildren(QPushButton):
            if "screen" in btn.text().lower():
                btn.pressed.connect(lambda: QTimer.singleShot(0, _enforcer.start))
                break

        _position_before_preview(dlg, self)

        def _live(c: QColor):
            self._field["color"] = c.name()
            self._refresh_color()
            if self._on_changed:
                self._on_changed()

        dlg.currentColorChanged.connect(_live)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            self._field["color"] = pre
            self._refresh_color()
            if self._on_changed:
                self._on_changed()
            return

        self._field["color"] = dlg.currentColor().name()
        self._refresh_color()
        if self._on_changed:
            self._on_changed()

    def _on_color_clicked(self):
        if is_audio_field(self._field.get("name", "")):
            self._edit_audio_colors()
        else:
            self._edit_color()

    def _refresh_audio_color_btn(self):
        active = bool(self._field.get("audio_icon_color") or self._field.get("audio_bg_color"))
        border = UI_ACCENT if active else UI_BORDER
        self._color_btn.setText("🎨")
        self._color_btn.setStyleSheet(
            f"QPushButton {{ border: {'2' if active else '1'}px solid {border}; border-radius: 4px;"
            f" background: {UI_BG_CARD}; font-size: 11px; padding: 0; }}"
            f"QPushButton:hover {{ border-color: {UI_ACCENT}; background: {UI_BG_HOVER}; }}"
            f"QPushButton:pressed {{ border-color: {UI_TEXT}; }}"
        )
        tip = "Audio colors"
        if self._field.get("audio_icon_color"):
            tip += f"\nIcon: {self._field['audio_icon_color']}"
        if self._field.get("audio_bg_color"):
            tip += f"\nBG: {self._field['audio_bg_color']}"
        self._color_btn.setToolTip(tip)

    def _edit_audio_colors(self):
        from aqt.qt import QFormLayout
        orig_icon = self._field.get("audio_icon_color")
        orig_bg   = self._field.get("audio_bg_color")

        dlg = QDialog(self)
        dlg.setWindowTitle("Audio Colors")
        dlg.setMinimumWidth(260)
        vl = QVBoxLayout(dlg)
        vl.setContentsMargins(12, 12, 12, 8)
        vl.setSpacing(8)

        form = QFormLayout()
        form.setSpacing(8)
        vl.addLayout(form)

        _icon = [self._field.get("audio_icon_color")]
        _bg   = [self._field.get("audio_bg_color")]

        def _swatch_style(color):
            if color:
                border = "#78889f" if _is_light(color) else "#2f3b4f"
                return (
                    f"QPushButton {{ background-color: {color}; border: 1px solid {border}; border-radius: 4px; }}"
                    f"QPushButton:hover {{ border-color: {UI_ACCENT}; }}"
                )
            return (
                f"QPushButton {{ background: {UI_BG_CARD}; border: 1px solid {UI_BORDER}; border-radius: 4px;"
                f" color: {UI_TEXT_MUTED}; font-size: 11px; }}"
                f"QPushButton:hover {{ border-color: {UI_ACCENT}; }}"
            )

        def _reset_btn_style():
            return (
                "QPushButton {"
                f" font-size: 10px; padding: 0 8px; height: 22px;"
                f" border: 1px solid {UI_BORDER}; border-radius: 3px;"
                f" background: {UI_BG_CARD}; color: {UI_TEXT_MUTED};"
                "}"
                f"QPushButton:hover {{ color: {UI_TEXT}; background: {UI_BG_HOVER}; }}"
            )

        # ── Icon color ──────────────────────────────────────────────────────
        icon_swatch = QPushButton()
        icon_swatch.setFixedSize(22, 22)
        icon_swatch.setCursor(Qt.CursorShape.PointingHandCursor)

        def _refresh_icon():
            icon_swatch.setStyleSheet(_swatch_style(_icon[0]))
            icon_swatch.setText("" if _icon[0] else "∅")

        _refresh_icon()

        def _pick_icon():
            start = QColor(_icon[0]) if _icon[0] else QColor("#1a1a1a")
            d = QColorDialog(start, dlg)
            d.setWindowTitle("Icon Color")
            d.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
            for box in d.findChildren(QDialogButtonBox):
                ok = box.button(QDialogButtonBox.StandardButton.Ok)
                if ok:
                    ok.setText("Save")
            pre = _icon[0]
            _position_before_preview(d, self)
            def _live_icon(c: QColor):
                _icon[0] = c.name()
                self._field["audio_icon_color"] = _icon[0]
                _refresh_icon()
                self._refresh_audio_color_btn()
                if self._on_changed:
                    self._on_changed()
            d.currentColorChanged.connect(_live_icon)
            if d.exec() != QDialog.DialogCode.Accepted:
                _icon[0] = pre
                self._field["audio_icon_color"] = pre
                _refresh_icon()
                self._refresh_audio_color_btn()
                if self._on_changed:
                    self._on_changed()
                return
            _icon[0] = d.currentColor().name()
            self._field["audio_icon_color"] = _icon[0]
            _refresh_icon()
            self._refresh_audio_color_btn()
            if self._on_changed:
                self._on_changed()

        icon_swatch.clicked.connect(_pick_icon)

        icon_reset = QPushButton("Reset")
        icon_reset.setStyleSheet(_reset_btn_style())
        def _do_reset_icon():
            _icon[0] = None
            _refresh_icon()
        icon_reset.clicked.connect(_do_reset_icon)

        icon_row = QWidget()
        icon_hl = QHBoxLayout(icon_row)
        icon_hl.setContentsMargins(0, 0, 0, 0)
        icon_hl.setSpacing(6)
        icon_hl.addWidget(icon_swatch)
        icon_hl.addWidget(icon_reset)
        icon_hl.addStretch()
        form.addRow("Icon color:", icon_row)

        # ── Background color ────────────────────────────────────────────────
        bg_swatch = QPushButton()
        bg_swatch.setFixedSize(22, 22)
        bg_swatch.setCursor(Qt.CursorShape.PointingHandCursor)

        def _refresh_bg():
            bg_swatch.setStyleSheet(_swatch_style(_bg[0]))
            bg_swatch.setText("" if _bg[0] else "∅")

        _refresh_bg()

        def _pick_bg():
            start = QColor(_bg[0]) if _bg[0] else QColor("#ffffff")
            d = QColorDialog(start, dlg)
            d.setWindowTitle("Background Color")
            d.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)
            for box in d.findChildren(QDialogButtonBox):
                ok = box.button(QDialogButtonBox.StandardButton.Ok)
                if ok:
                    ok.setText("Save")
            pre = _bg[0]
            _position_before_preview(d, self)
            def _live_bg(c: QColor):
                _bg[0] = c.name()
                self._field["audio_bg_color"] = _bg[0]
                _refresh_bg()
                self._refresh_audio_color_btn()
                if self._on_changed:
                    self._on_changed()
            d.currentColorChanged.connect(_live_bg)
            if d.exec() != QDialog.DialogCode.Accepted:
                _bg[0] = pre
                self._field["audio_bg_color"] = pre
                _refresh_bg()
                self._refresh_audio_color_btn()
                if self._on_changed:
                    self._on_changed()
                return
            _bg[0] = d.currentColor().name()
            self._field["audio_bg_color"] = _bg[0]
            _refresh_bg()
            self._refresh_audio_color_btn()
            if self._on_changed:
                self._on_changed()

        bg_swatch.clicked.connect(_pick_bg)

        bg_reset = QPushButton("Reset")
        bg_reset.setStyleSheet(_reset_btn_style())
        def _do_reset_bg():
            _bg[0] = None
            _refresh_bg()
        bg_reset.clicked.connect(_do_reset_bg)

        bg_row = QWidget()
        bg_hl = QHBoxLayout(bg_row)
        bg_hl.setContentsMargins(0, 0, 0, 0)
        bg_hl.setSpacing(6)
        bg_hl.addWidget(bg_swatch)
        bg_hl.addWidget(bg_reset)
        bg_hl.addStretch()
        form.addRow("Background:", bg_row)

        # ── Save / Cancel ───────────────────────────────────────────────────
        btns = QDialogButtonBox()
        save_btn   = btns.addButton("Save",   QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_btn = btns.addButton(QDialogButtonBox.StandardButton.Cancel)
        save_btn.clicked.connect(dlg.accept)
        cancel_btn.clicked.connect(dlg.reject)
        vl.addWidget(btns)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._field["audio_icon_color"] = _icon[0]
            self._field["audio_bg_color"]   = _bg[0]
            self._refresh_audio_color_btn()
            if self._on_changed:
                self._on_changed()
        else:
            self._field["audio_icon_color"] = orig_icon
            self._field["audio_bg_color"]   = orig_bg
            self._refresh_audio_color_btn()
            if self._on_changed:
                self._on_changed()

    def _size_changed(self, val: int):
        self._field["font_size"] = val
        self._refresh_font_button()
        if self._on_changed:
            self._on_changed()

    def _is_media_field(self) -> bool:
        name = self._field.get("name", "")
        return is_audio_field(name) or is_image_field(name)

    def _refresh_compare_chip(self) -> None:
        if self._compare_chip is None:
            return
        cf = self._field.get("compare_field", "")
        if cf:
            self._compare_chip.setText(f"vs {{{{{cf}}}}}")
            self._compare_chip.setStyleSheet(
                f"color: white; background: {UI_ACCENT}; font-size: 9px; font-weight: 600;"
                " border-radius: 4px; padding: 1px 6px;"
            )
        else:
            self._compare_chip.setText("no field ▾")
            self._compare_chip.setStyleSheet(
                f"color: {UI_TEXT_MUTED}; background: {UI_BG_HOVER};"
                f" border: 1px solid {UI_BORDER}; font-size: 9px;"
                " border-radius: 4px; padding: 1px 6px;"
            )

    def _refresh_control_mode(self) -> None:
        if self._field.get("virtual"):
            self._color_btn.setVisible(False)
            self._font_btn.setVisible(False)
            self._align_btn.setVisible(False)
            self._spin.setVisible(False)
            self._media_size_btn.setVisible(False)
            self._spacing_btn.setVisible(False)
            return
        name  = self._field.get("name", "")
        audio = is_audio_field(name)
        image = is_image_field(name)
        media = audio or image
        self._color_btn.setVisible(not image)
        self._font_btn.setVisible(not media)
        self._spin.setVisible(not media)
        self._media_size_btn.setVisible(media)
        if media:
            self._refresh_media_size_button()
        if audio:
            self._refresh_audio_color_btn()
        elif not image:
            self._refresh_color()

    def _refresh_media_size_button(self) -> None:
        is_audio = is_audio_field(self._field.get("name", ""))
        hidden   = is_audio and self._field.get("audio_hidden", False)
        border   = UI_ACCENT if hidden else UI_BORDER
        self._media_size_btn.setStyleSheet(
            "QPushButton {"
            f" border: 1px solid {border}; border-radius: 4px;"
            f" background: {UI_BG_CARD}; color: {'%s' % (UI_TEXT_MUTED if hidden else UI_TEXT)};"
            " font-size: 10px; font-weight: 600; padding: 0 4px;"
            "}"
            "QPushButton:hover {"
            f" border-color: {UI_BORDER_STRONG}; background: {UI_BG_HOVER};"
            "}"
        )
        if hidden:
            self._media_size_btn.setText("Hidden")
            self._media_size_btn.setToolTip("Audio hidden on card — click to edit")
            return
        width = self._field.get("media_width")
        height = self._field.get("media_height")
        if isinstance(width, int) and isinstance(height, int):
            self._media_size_btn.setText(f"{width}x{height}")
            self._media_size_btn.setToolTip(f"Set media size: {width}x{height}px")
        else:
            self._media_size_btn.setText("Size")
            self._media_size_btn.setToolTip("Set media width/height")

    def _edit_media_size(self) -> None:
        from aqt.qt import QFormLayout

        is_audio  = is_audio_field(self._field.get("name", ""))
        default_w = 280 if is_audio else 200
        default_h = 32  if is_audio else 200
        original_w      = self._field.get("media_width",  default_w)
        original_h      = self._field.get("media_height", default_h)
        original_hidden = self._field.get("audio_hidden", False) if is_audio else False

        dlg = QDialog(self)
        dlg.setWindowTitle("Set audio size" if is_audio else "Set media size")
        vl = QVBoxLayout(dlg)
        vl.setContentsMargins(14, 14, 14, 10)
        vl.setSpacing(8)

        size_form = QFormLayout()
        size_form.setSpacing(6)
        vl.addLayout(size_form)

        w_spin = QSpinBox(dlg)
        w_spin.setRange(24, 1400)
        w_spin.setSuffix("px")
        w_spin.setValue(self._field.get("media_width", default_w))

        h_spin = QSpinBox(dlg)
        h_spin.setRange(16, 1400)
        h_spin.setSuffix("px")
        h_spin.setValue(self._field.get("media_height", default_h))

        def _apply_size_live() -> None:
            self._field["media_width"]  = w_spin.value()
            self._field["media_height"] = h_spin.value()
            self._refresh_media_size_button()
            if self._on_changed:
                self._on_changed()

        w_spin.valueChanged.connect(lambda _=None: _apply_size_live())
        h_spin.valueChanged.connect(lambda _=None: _apply_size_live())
        size_form.addRow("Width:", w_spin)
        size_form.addRow("Height:", h_spin)

        if is_audio:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setFrameShadow(QFrame.Shadow.Sunken)
            vl.addWidget(sep)

            hide_check = QCheckBox("Hide audio on card")
            hide_check.setChecked(self._field.get("audio_hidden", False))
            def _on_hide(state):
                self._field["audio_hidden"] = hide_check.isChecked()
                self._refresh_media_size_button()
                if self._on_changed:
                    self._on_changed()
            hide_check.stateChanged.connect(_on_hide)
            vl.addWidget(hide_check)

        btns = QDialogButtonBox()
        save_btn   = btns.addButton("Save",          QDialogButtonBox.ButtonRole.AcceptRole)
        reset_btn  = btns.addButton("Reset default", QDialogButtonBox.ButtonRole.ResetRole)
        cancel_btn = btns.addButton(QDialogButtonBox.StandardButton.Cancel)
        save_btn.clicked.connect(dlg.accept)
        cancel_btn.clicked.connect(dlg.reject)

        def _reset_default() -> None:
            w_spin.setValue(default_w)
            h_spin.setValue(default_h)

        reset_btn.clicked.connect(_reset_default)
        vl.addWidget(btns)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            self._field["media_width"]  = original_w
            self._field["media_height"] = original_h
            if is_audio:
                self._field["audio_hidden"] = original_hidden
            self._refresh_media_size_button()
            if self._on_changed:
                self._on_changed()
            return

        self._field["media_width"]  = w_spin.value()
        self._field["media_height"] = h_spin.value()
        self._refresh_media_size_button()
        if self._on_changed:
            self._on_changed()

    def _refresh_spacing_button(self) -> None:
        pv = self._field.get("padding_v", 0)
        ph = self._field.get("padding_h", 0)
        mt = self._field.get("margin_top", 0)
        mb = self._field.get("margin_bottom", 0)
        has_spacing = bool(pv or ph or mt or mb)
        border = UI_ACCENT if has_spacing else UI_BORDER
        self._spacing_btn.setStyleSheet(
            "QPushButton {"
            f" border: 1px solid {border}; border-radius: 4px;"
            f" background: {UI_BG_CARD}; color: {UI_TEXT};"
            " font-size: 10px; font-weight: 600; padding: 0 4px;"
            "}"
            "QPushButton:hover {"
            f" border-color: {UI_BORDER_STRONG}; background: {UI_BG_HOVER};"
            "}"
        )
        self._spacing_btn.setToolTip(
            f"Padding: {pv}px top/bottom, {ph}px left/right\n"
            f"Margin: {mt}px top, {mb}px bottom"
        )

    def _edit_spacing(self) -> None:
        from aqt.qt import QFormLayout

        is_media = self._is_media_field()
        original = {
            "padding_v":    self._field.get("padding_v", 0),
            "padding_h":    self._field.get("padding_h", 0),
            "margin_top":   self._field.get("margin_top", 0),
            "margin_bottom": self._field.get("margin_bottom", 0),
        }

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Spacing — {self._field.get('name', '')}")
        form = QFormLayout(dlg)
        form.setContentsMargins(14, 14, 14, 14)
        form.setSpacing(8)

        def _spinbox(val: int) -> QSpinBox:
            s = QSpinBox(dlg)
            s.setRange(-200, 200)
            s.setSuffix("px")
            s.setValue(val)
            return s

        pv_spin = _spinbox(original["padding_v"])
        ph_spin = _spinbox(original["padding_h"])
        mt_spin = _spinbox(original["margin_top"])
        mb_spin = _spinbox(original["margin_bottom"])

        def _apply_live() -> None:
            self._field["padding_v"]    = pv_spin.value()
            self._field["padding_h"]    = ph_spin.value()
            self._field["margin_top"]   = mt_spin.value()
            self._field["margin_bottom"] = mb_spin.value()
            self._refresh_spacing_button()
            if self._on_changed:
                self._on_changed()

        pv_spin.valueChanged.connect(lambda _=None: _apply_live())
        ph_spin.valueChanged.connect(lambda _=None: _apply_live())
        mt_spin.valueChanged.connect(lambda _=None: _apply_live())
        mb_spin.valueChanged.connect(lambda _=None: _apply_live())

        form.addRow("Padding top & bottom:", pv_spin)
        form.addRow("Padding left & right:", ph_spin)
        form.addRow("Margin top:", mt_spin)
        form.addRow("Margin bottom:", mb_spin)

        btns = QDialogButtonBox()
        save_btn   = btns.addButton("Save",  QDialogButtonBox.ButtonRole.AcceptRole)
        reset_btn  = btns.addButton("Reset", QDialogButtonBox.ButtonRole.ResetRole)
        cancel_btn = btns.addButton(QDialogButtonBox.StandardButton.Cancel)
        save_btn.clicked.connect(dlg.accept)
        cancel_btn.clicked.connect(dlg.reject)

        def _reset() -> None:
            pv_spin.setValue(0)
            ph_spin.setValue(0)
            mt_spin.setValue(0)
            mb_spin.setValue(0)

        reset_btn.clicked.connect(_reset)
        form.addRow(btns)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            for k, v in original.items():
                self._field[k] = v
            self._refresh_spacing_button()
            if self._on_changed:
                self._on_changed()
            return

        _apply_live()

    def _font_from_field(self) -> QFont:
        font = QFont()
        family = self._field.get("font_family")
        if isinstance(family, str) and family.strip():
            font.setFamily(family.strip())

        size = self._field.get("font_size")
        if isinstance(size, int) and size > 0:
            font.setPointSize(size)

        weight = self._field.get("font_weight")
        if isinstance(weight, int) and 1 <= weight <= 1000:
            font.setWeight(weight)

        italic = self._field.get("font_italic")
        if isinstance(italic, bool):
            font.setItalic(italic)
        return font

    def _refresh_font_button(self) -> None:
        family = self._field.get("font_family", "")
        has_family = isinstance(family, str) and bool(family.strip())
        style_parts = []

        italic = self._field.get("font_italic")
        if italic is True:
            style_parts.append("Italic")

        weight = self._field.get("font_weight")
        if isinstance(weight, int):
            if weight >= 700:
                style_parts.append("Bold")
            elif weight <= 350:
                style_parts.append("Light")
            else:
                style_parts.append("Regular")

        size = self._field.get("font_size")
        size_txt = f"{size}px" if isinstance(size, int) and size > 0 else None

        if has_family:
            details = [family.strip()]
            if style_parts:
                details.append(" ".join(style_parts))
            if size_txt:
                details.append(size_txt)
            self._font_btn.setToolTip(" | ".join(details))
        else:
            self._font_btn.setToolTip("Choose font for this field")

    def apply_styles(self, styles: dict) -> None:
        _STYLE_KEYS = {
            "color", "font_size", "font_family", "font_weight", "font_italic",
            "align", "padding_v", "padding_h", "margin_top", "margin_bottom",
            "media_width", "media_height", "audio_icon_color", "audio_bg_color", "audio_hidden",
        }
        for k in _STYLE_KEYS:
            if k in styles:
                self._field[k] = styles[k]
        self._refresh_control_mode()
        align = self._field.get("align", "left")
        if align in ("left", "center", "right"):
            self._set_align(align, notify=False)
        self._spin.blockSignals(True)
        self._spin.setValue(self._field.get("font_size", 16))
        self._spin.blockSignals(False)
        self._refresh_font_button()
        self._refresh_spacing_button()

    def _cycle_align(self):
        order = ("left", "center", "right")
        current = self._field.get("align", "left")
        try:
            idx = order.index(current)
        except ValueError:
            idx = 0
        self._set_align(order[(idx + 1) % len(order)])

    def _set_align(self, align: str, notify: bool = True):
        self._field["align"] = align
        tip = {"left": "Align left", "center": "Align center", "right": "Align right"}.get(align, "Align")
        self._align_btn.set_align(align)
        self._align_btn.setToolTip(tip)
        if notify and self._on_changed:
            self._on_changed()

    def _pick_font_family(self):
        original = {
            "font_family": self._field.get("font_family"),
            "font_weight": self._field.get("font_weight"),
            "font_italic": self._field.get("font_italic"),
            "font_size":   self._field.get("font_size"),
        }

        dlg = QFontDialog(self)
        dlg.setWindowTitle("Select font")
        dlg.setCurrentFont(self._font_from_field())
        dlg.setOption(QFontDialog.FontDialogOption.DontUseNativeDialog, True)

        for box in dlg.findChildren(QDialogButtonBox):
            ok_btn = box.button(QDialogButtonBox.StandardButton.Ok)
            if ok_btn:
                ok_btn.setText("Save")

        def _apply_live(font: QFont) -> None:
            self._field["font_family"] = font.family()
            self._field["font_weight"] = font.weight()
            self._field["font_italic"] = font.italic()
            size = font.pointSize()
            if size > 0:
                self._field["font_size"] = size
                self._spin.blockSignals(True)
                self._spin.setValue(size)
                self._spin.blockSignals(False)
            self._refresh_font_button()
            if self._on_changed:
                self._on_changed()

        dlg.currentFontChanged.connect(_apply_live)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            for k, v in original.items():
                if v is None:
                    self._field.pop(k, None)
                else:
                    self._field[k] = v
            orig_size = original.get("font_size")
            if isinstance(orig_size, int) and orig_size > 0:
                self._spin.blockSignals(True)
                self._spin.setValue(orig_size)
                self._spin.blockSignals(False)
            self._refresh_font_button()
            if self._on_changed:
                self._on_changed()
            return

        self._refresh_font_button()
        if self._on_changed:
            self._on_changed()

    # ── Drag ───────────────────────────────────────────────────────────────────

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            pos = event.position().toPoint()
            spacing_w = self.SPACING_BTN_W + 6
            if self._is_media_field():
                control_w = spacing_w + self.SIZE_BTN_W + 6 + self.ALIGN_W + 6
            else:
                control_w = spacing_w + self.SPIN_W + 6 + self.FONT_W + 6 + self.ALIGN_W + 6 + self.COLOR_W + 6
            drag_boundary = self.width() - 8 - control_w
            if pos.x() < drag_boundary:
                self._drag_start = pos
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if (
            self._drag_start is not None
            and bool(event.buttons() & Qt.MouseButton.LeftButton)
            and (event.position().toPoint() - self._drag_start).manhattanLength() >= 6
        ):
            self._do_drag()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_start = None
        super().mouseReleaseEvent(event)

    def _do_drag(self) -> None:
        self._drag_start = None
        drag = QDrag(self)
        mime = QMimeData()
        mime.setData(FIELD_MIME, json.dumps(self._field).encode())
        drag.setMimeData(mime)
        px = self.grab()
        drag.setPixmap(px)
        drag.setHotSpot(QPoint(px.width() // 4, px.height() // 2))
        drag.exec(Qt.DropAction.MoveAction)


# ─── Field List Widget ────────────────────────────────────────────────────────

class FieldListWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setStyleSheet(
            "FieldListWidget {"
            f" background: transparent; border: 1px solid {UI_BORDER}; border-radius: 8px;"
            "}"
        )

        self._vbox = QVBoxLayout(self)
        self._vbox.setContentsMargins(4, 4, 4, 4)
        self._vbox.setSpacing(2)
        self._vbox.addStretch()

        self._rows: list[FieldRowWidget] = []
        self._drop_idx: int | None = None
        self.on_changed = None
        self._is_mapping_list: bool = False
        self._role: str = ""
        self.on_virtual_drop = None  # Callable[[dict], dict | None]

    # ── Public API ─────────────────────────────────────────────────────────────

    def clear(self):
        for row in list(self._rows):
            self._vbox.removeWidget(row)
            row.deleteLater()
        self._rows.clear()

    def add_field(self, field: dict):
        self._insert_at(len(self._rows), field)

    def insert_field(self, idx: int, field: dict):
        self._insert_at(idx, field)

    def remove_row_widget(self, row: FieldRowWidget):
        if row in self._rows:
            self._rows.remove(row)
            self._vbox.removeWidget(row)
            row.deleteLater()
            self._adjust_height()

    def get_fields(self) -> list[dict]:
        return [r.get_field() for r in self._rows]

    def recolor(self, color: str):
        for row in self._rows:
            row.set_color(color)

    def refresh_dimmed(self, front_names: set) -> None:
        for row in self._rows:
            row.set_dimmed(row.get_field()["name"] in front_names)

    # ── Private ────────────────────────────────────────────────────────────────

    def _insert_at(self, idx: int, field: dict):
        idx = max(0, min(idx, len(self._rows)))
        row = FieldRowWidget(field, on_changed=self._notify)
        self._rows.insert(idx, row)
        self._vbox.insertWidget(idx, row)
        self._adjust_height()

    def _notify(self):
        if self.on_changed:
            self.on_changed()

    def _adjust_height(self):
        h = len(self._rows) * (FieldRowWidget.ROW_H + 2) + 8
        self.setMinimumHeight(max(50, min(200, h)))

    def _row_at(self, pos: QPoint) -> int:
        for i, row in enumerate(self._rows):
            if pos.y() < row.y() + row.height() // 2:
                return i
        return len(self._rows)

    # ── Drag & Drop ────────────────────────────────────────────────────────────

    def dragEnterEvent(self, event) -> None:
        if event.mimeData().hasFormat(FIELD_MIME):
            event.acceptProposedAction()

    def dragMoveEvent(self, event) -> None:
        if event.mimeData().hasFormat(FIELD_MIME):
            self._drop_idx = self._row_at(event.position().toPoint())
            self.update()
            event.acceptProposedAction()

    def dragLeaveEvent(self, event) -> None:
        self._drop_idx = None
        self.update()

    def dropEvent(self, event) -> None:
        if not event.mimeData().hasFormat(FIELD_MIME):
            return
        field    = json.loads(event.mimeData().data(FIELD_MIME).data().decode())
        drop_idx = self._row_at(event.position().toPoint())

        src = event.source()
        src_list = None
        src_idx  = -1
        if isinstance(src, FieldRowWidget):
            candidate = src.parent()
            if isinstance(candidate, FieldListWidget):
                src_list = candidate
                src_idx  = src_list._rows.index(src) if src in src_list._rows else -1

        if self._role == "back" and field.get("name") == _TYPE_ANSWER_BOX:
            self._drop_idx = None
            self.update()
            QMessageBox.warning(
                self,
                "Cannot Place Here",
                '"✍️ Type Answer Box" can only be placed on the Front side.',
            )
            return

        if (field.get("virtual") and self._is_mapping_list
                and self.on_virtual_drop and src_list is not self):
            updated = self.on_virtual_drop(field)
            if updated is None:
                self._drop_idx = None
                self.update()
                return
            field = updated

        if src_list:
            src_list.remove_row_widget(src)
            if src_list is self and src_idx >= 0 and src_idx < drop_idx:
                drop_idx -= 1

        self.insert_field(drop_idx, field)
        self._drop_idx = None
        self.update()
        event.acceptProposedAction()
        if self.on_changed:
            self.on_changed()

    def paintEvent(self, event) -> None:
        super().paintEvent(event)
        if self._drop_idx is None:
            return
        p = QPainter(self)
        p.setPen(QPen(QColor(UI_ACCENT), 2))
        y = self._rows[self._drop_idx].y() if self._drop_idx < len(self._rows) else self.height() - 6
        p.drawLine(8, y, self.width() - 8, y)
        p.end()


# ─── Restore Dialog ───────────────────────────────────────────────────────────

class RestoreDialog(QDialog):
    def __init__(self, parent, backups: list):
        super().__init__(parent)
        self.setWindowTitle("Restore Backup")
        self.setMinimumWidth(500)
        self.selected_id = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Select a backup to restore:"))

        self.list = QListWidget()
        for b in backups:
            item = QListWidgetItem(
                f"{b['timestamp']}  —  {b['model_name']} / {b['tmpl_name']}"
            )
            item.setData(Qt.ItemDataRole.UserRole, b["id"])
            self.list.addItem(item)
        layout.addWidget(self.list)

        note = QLabel("Only the 5 most recent backups are kept across all Note Types.")
        note.setStyleSheet("color: gray; font-size: 11px;")
        layout.addWidget(note)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self._on_ok)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _on_ok(self):
        item = self.list.currentItem()
        if not item:
            QMessageBox.warning(self, "No Selection", "Please select a backup.")
            return
        self.selected_id = item.data(Qt.ItemDataRole.UserRole)
        self.accept()


# ─── Type Answer Field Picker ─────────────────────────────────────────────────

class TypeAnswerFieldDialog(QDialog):
    def __init__(self, parent, available_fields: list, current_field: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Type Answer Box — Configure")
        self.setFixedWidth(380)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)

        hint = QLabel(
            "Select the field that contains the correct answer. "
            "For example, if you need to type 'apple', select the field that holds 'apple'."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {UI_TEXT_MUTED}; font-size: 11px;")
        layout.addWidget(hint)

        self._combo = QComboBox()
        self._combo.addItems(available_fields)
        if current_field in available_fields:
            self._combo.setCurrentText(current_field)
        layout.addWidget(self._combo)

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def selected_field(self) -> str:
        return self._combo.currentText()


# ─── Main Dialog ──────────────────────────────────────────────────────────────

class PrettifyDialog(QDialog):
    PREVIEW_MIN_WIDTH  = 390  # mobile-like viewport width
    LEFT_PANEL_MIN_W   = 430  # wide enough to show all controls without clipping
    _DEFAULT_CARD_BG_OPACITY = 0.75

    def __init__(self, parent=None, initial_note_type: str | None = None, initial_card_tmpl_ord: int = 0):
        super().__init__(parent)
        self.setWindowTitle("Clazure Design")
        self.setMinimumSize(980, 660)

        self._note_model: dict | None = None
        self._card_tmpl:  dict | None = None
        self._tmpl_cfg:   dict | None = None
        self._front_fields: list[dict] = []
        self._back_fields:  list[dict] = []
        self._note_type_fields: list[str] = []
        self._initial_note_type = initial_note_type
        self._initial_card_tmpl_ord = initial_card_tmpl_ord
        self._card_bg_color: str | None = None
        self._card_bg_opacity: float = self._DEFAULT_CARD_BG_OPACITY
        self._card_bg_is_custom: bool = False
        self._card_bg_dark_color: str | None = None
        self._card_bg_dark_opacity: float = self._DEFAULT_CARD_BG_OPACITY
        self._card_bg_dark_is_custom: bool = False
        self._card_bg_by_template: dict[str, dict] = {}
        self._hr_style: dict | None = None

        self._has_applied = False

        self._dark = _is_night_mode()
        _apply_theme(self._dark)
        self._setup_ui()
        self._load_prettify_templates()
        self._load_note_types()

    # ── UI Construction ────────────────────────────────────────────────────────

    def _dark_global_stylesheet(self) -> str:
        return f"""
            QLabel {{ color: {UI_TEXT}; background: transparent; }}
            QComboBox {{
                background: {UI_BG_MAIN};
                border: 1px solid {UI_BORDER};
                border-radius: 4px;
                padding: 4px 8px;
                color: {UI_TEXT};
                min-height: 24px;
            }}
            QComboBox:hover {{ border-color: {UI_BORDER_STRONG}; }}
            QComboBox:focus {{ border-color: {UI_ACCENT}; }}
            QComboBox::drop-down {{ border: none; width: 18px; }}
            QComboBox QAbstractItemView {{
                background: {UI_BG_CARD};
                border: 1px solid {UI_BORDER_STRONG};
                selection-background-color: {UI_ACCENT};
                selection-color: white;
                outline: none;
                padding: 2px;
            }}
            QSpinBox, QDoubleSpinBox {{
                background: {UI_BG_MAIN};
                border: 1px solid {UI_BORDER};
                border-radius: 4px;
                padding: 3px 6px;
                color: {UI_TEXT};
                min-height: 22px;
            }}
            QSpinBox:hover, QDoubleSpinBox:hover {{ border-color: {UI_BORDER_STRONG}; }}
            QSpinBox:focus, QDoubleSpinBox:focus {{ border-color: {UI_ACCENT}; }}
            QScrollBar:vertical {{
                background: {UI_BG_MAIN};
                width: 6px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {UI_BORDER_STRONG};
                border-radius: 3px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {UI_TEXT_MUTED}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}
            QSplitter::handle {{ background: {UI_BORDER}; }}
            QTabWidget::pane {{
                border: 1px solid {UI_BORDER};
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background: {UI_BG_CARD};
                color: {UI_TEXT_MUTED};
                border: 1px solid {UI_BORDER};
                border-bottom: none;
                padding: 5px 18px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background: {UI_ACCENT};
                color: white;
                border-color: {UI_ACCENT};
            }}
            QTabBar::tab:hover:!selected {{
                background: {UI_BG_HOVER};
                color: {UI_TEXT};
            }}
            QPushButton {{
                background: {UI_BG_CARD};
                border: 1px solid {UI_BORDER};
                border-radius: 4px;
                color: {UI_TEXT};
                padding: 5px 14px;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background: {UI_BG_HOVER};
                border-color: {UI_BORDER_STRONG};
            }}
            QPushButton:pressed {{ background: {UI_BG_LIST}; }}
            QListWidget {{
                background: {UI_BG_CARD};
                border: 1px solid {UI_BORDER};
                border-radius: 4px;
                color: {UI_TEXT};
                outline: none;
            }}
            QListWidget::item:selected {{
                background: {UI_ACCENT};
                color: white;
            }}
            QListWidget::item:hover {{
                background: {UI_BG_HOVER};
            }}
        """

    def _setup_ui(self):
        if self._dark:
            self.setStyleSheet(self._dark_global_stylesheet())
        root = QHBoxLayout(self)
        root.setSpacing(0)
        root.setContentsMargins(0, 0, 0, 0)

        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)
        self.main_splitter.addWidget(self._build_left_panel())
        self.main_splitter.addWidget(self._build_right_panel())
        self.main_splitter.setStretchFactor(0, 0)
        self.main_splitter.setStretchFactor(1, 1)
        self.main_splitter.setSizes([self.LEFT_PANEL_MIN_W, self.PREVIEW_MIN_WIDTH])
        self.main_splitter.setCollapsible(0, False)
        self.main_splitter.setCollapsible(1, False)

        root.addWidget(self.main_splitter)
        self._restore_splitter_sizes()

    def _build_left_panel(self) -> QWidget:
        outer = QWidget()
        outer.setMinimumWidth(self.LEFT_PANEL_MIN_W)
        outer.setStyleSheet(f"background: {UI_BG_PANEL};")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        layout = QVBoxLayout(inner)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(10)

        layout.addWidget(self._build_note_section())
        layout.addWidget(self._build_template_section())
        layout.addWidget(self._build_mapping_section())
        layout.addStretch()
        layout.addWidget(self._build_action_buttons())

        scroll.setWidget(inner)

        vbox = QVBoxLayout(outer)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.addWidget(scroll)
        return outer

    def _build_right_panel(self) -> QWidget:
        panel = QWidget()
        panel.setMinimumWidth(self.PREVIEW_MIN_WIDTH)
        panel.setStyleSheet(f"background: {UI_BG_MAIN};")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(14, 14, 14, 14)

        hdr = QLabel("Preview")
        hdr.setStyleSheet(f"font-weight: bold; font-size: 13px; color: {UI_TEXT_MUTED};")
        layout.addWidget(hdr)

        self.preview_tabs  = QTabWidget()
        self.preview_front = self._make_webview()
        self.preview_back  = self._make_webview()
        self.preview_tabs.addTab(self.preview_front, "Front")
        self.preview_tabs.addTab(self.preview_back,  "Back")
        self.preview_tabs.currentChanged.connect(self._refresh_preview)
        layout.addWidget(self.preview_tabs)
        return panel

    def _make_webview(self):
        placeholder = (
            "<p style='color:#aaa;text-align:center;padding:60px 20px;"
            "font-family:sans-serif'>Select a template to preview</p>"
        )
        try:
            from aqt.webview import AnkiWebView
            w = AnkiWebView(parent=self)
            w.setHtml(placeholder)
            return w
        except Exception:
            from aqt.qt import QTextEdit
            w = QTextEdit()
            w.setReadOnly(True)
            w.setHtml(placeholder)
            return w

    def _set_html(self, widget, html: str):
        try:
            widget.setHtml(html)
        except Exception:
            pass

    # ── Sections ───────────────────────────────────────────────────────────────

    def _make_group(self, title: str) -> QGroupBox:
        box = QGroupBox(title)
        box.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold; font-size: 11px; color: {UI_TEXT};
                border: 1px solid {UI_BORDER}; border-radius: 8px;
                margin-top: 6px; padding-top: 6px; background: transparent;
            }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 4px; }}
        """)
        return box

    def _build_note_section(self) -> QGroupBox:
        box = self._make_group("Note Type")
        from aqt.qt import QFormLayout
        form = QFormLayout(box)
        form.setContentsMargins(10, 14, 10, 10)

        self.note_type_combo = QComboBox()
        self.note_type_combo.currentIndexChanged.connect(self._on_note_type_changed)
        form.addRow("Note Type:", self.note_type_combo)

        self.card_tmpl_combo = QComboBox()
        self.card_tmpl_combo.currentIndexChanged.connect(self._on_card_tmpl_changed)
        form.addRow("Card Template:", self.card_tmpl_combo)
        return box

    def _build_template_section(self) -> QGroupBox:
        box = self._make_group("Prettify Template")
        vbox = QVBoxLayout(box)
        vbox.setContentsMargins(10, 14, 10, 10)

        self.prettify_combo = NoWheelComboBox()
        self.prettify_combo.currentIndexChanged.connect(self._on_prettify_changed)
        vbox.addWidget(self.prettify_combo)

        self.tmpl_desc = QLabel("")
        self.tmpl_desc.setWordWrap(True)
        self.tmpl_desc.setStyleSheet(f"color: {UI_TEXT_MUTED}; font-size: 11px;")
        vbox.addWidget(self.tmpl_desc)

        lh_row = QWidget()
        lh_hl = QHBoxLayout(lh_row)
        lh_hl.setContentsMargins(0, 4, 0, 0)
        lh_hl.setSpacing(2)

        lh_lbl = QLabel("Text line height:")
        lh_lbl.setFixedWidth(100)
        lh_lbl.setStyleSheet(f"font-size: 11px; color: {UI_TEXT};")
        lh_hl.addWidget(lh_lbl)

        self._line_height_spin = LineHeightSpinBox()
        self._line_height_spin.setValue(1.0)
        self._line_height_spin.connect(self._refresh_preview)
        self._line_height_spin.connect(self._save_note_state)
        lh_hl.addWidget(self._line_height_spin)
        lh_hl.addStretch()
        vbox.addWidget(lh_row)

        # Field gap row
        gap_row = QWidget()
        gap_hl  = QHBoxLayout(gap_row)
        gap_hl.setContentsMargins(0, 4, 0, 0)
        gap_hl.setSpacing(2)

        gap_lbl = QLabel("Field gap:")
        gap_lbl.setFixedWidth(100)
        gap_lbl.setStyleSheet(f"font-size: 11px; color: {UI_TEXT};")
        gap_hl.addWidget(gap_lbl)

        self._field_gap_spin = NoWheelSpinBox()
        self._field_gap_spin.setRange(-1, 64)
        self._field_gap_spin.setSingleStep(4)
        self._field_gap_spin.setSpecialValueText("Auto")
        self._field_gap_spin.setValue(-1)
        self._field_gap_spin.setFixedWidth(60)
        self._field_gap_spin.setFixedHeight(22)
        self._field_gap_spin.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._field_gap_spin.setStyleSheet(
            f"QSpinBox {{ font-size: 11px; color: {UI_TEXT}; background: {UI_BG_CARD};"
            f" border: 1px solid {UI_BORDER}; border-radius: 4px; padding: 0 4px; }}"
        )
        self._field_gap_spin.valueChanged.connect(self._refresh_preview)
        self._field_gap_spin.valueChanged.connect(self._save_note_state)
        gap_hl.addWidget(self._field_gap_spin)

        gap_lbl2 = QLabel("px")
        gap_lbl2.setStyleSheet(f"font-size: 11px; color: {UI_TEXT_MUTED};")
        gap_hl.addWidget(gap_lbl2)

        gap_hl.addStretch()
        vbox.addWidget(gap_row)

        # Card BG row
        bg_row = QWidget()
        bg_hl  = QHBoxLayout(bg_row)
        bg_hl.setContentsMargins(0, 4, 0, 0)
        bg_hl.setSpacing(2)

        bg_lbl = QLabel("Card BG:")
        bg_lbl.setFixedWidth(100)
        bg_lbl.setStyleSheet(f"font-size: 11px; color: {UI_TEXT};")
        bg_hl.addWidget(bg_lbl)

        self._card_bg_btn = QPushButton()
        self._card_bg_btn.setFixedSize(22, 22)
        self._card_bg_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._card_bg_btn.clicked.connect(self._pick_card_bg)
        self._refresh_card_bg_btn()
        bg_hl.addWidget(self._card_bg_btn)

        self._card_bg_slider = QSlider(Qt.Orientation.Horizontal)
        self._card_bg_slider.setRange(0, 100)
        self._card_bg_slider.setValue(int(self._DEFAULT_CARD_BG_OPACITY * 100))
        self._card_bg_slider.setFixedWidth(90)
        self._card_bg_slider.valueChanged.connect(self._on_card_bg_opacity)
        bg_hl.addWidget(self._card_bg_slider)

        self._card_bg_pct = QLabel(f"{int(self._DEFAULT_CARD_BG_OPACITY * 100)}%")
        self._card_bg_pct.setFixedWidth(34)
        self._card_bg_pct.setStyleSheet(f"font-size: 11px; color: {UI_TEXT};")
        bg_hl.addWidget(self._card_bg_pct)

        card_bg_reset = QPushButton("Reset")
        card_bg_reset.setFixedHeight(22)
        card_bg_reset.setStyleSheet(
            "QPushButton {"
            f" font-size: 10px; padding: 0 8px;"
            f" border: 1px solid {UI_BORDER}; border-radius: 3px;"
            f" background: {UI_BG_CARD}; color: {UI_TEXT_MUTED};"
            "}"
            f"QPushButton:hover {{ color: {UI_TEXT}; background: {UI_BG_HOVER}; }}"
        )
        card_bg_reset.clicked.connect(self._reset_card_bg)
        bg_hl.addWidget(card_bg_reset)

        bg_hl.addStretch()
        vbox.addWidget(bg_row)

        # Divider row
        div_row = QWidget()
        div_hl  = QHBoxLayout(div_row)
        div_hl.setContentsMargins(0, 4, 0, 0)
        div_hl.setSpacing(2)

        div_lbl = QLabel("Divider:")
        div_lbl.setFixedWidth(100)
        div_lbl.setStyleSheet(f"font-size: 11px; color: {UI_TEXT};")
        div_hl.addWidget(div_lbl)

        self._hr_style_btn = QPushButton("Default")
        self._hr_style_btn.setFixedHeight(22)
        self._hr_style_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self._hr_style_btn.clicked.connect(self._edit_hr_style)
        self._refresh_hr_btn()
        div_hl.addWidget(self._hr_style_btn)

        div_hl.addStretch()
        vbox.addWidget(div_row)

        return box

    # ── Card BG helpers ────────────────────────────────────────────────────────

    _TEMPLATE_BG_DARK = {
        "Minimal": "#2A2B2D",
        "Nord":    "#2B313C",
        "Dracula": "#282a36",
    }
    _TEMPLATE_BG_LIGHT = {
        "Minimal": "#F5EFDF",
        "Nord":    "#FFFFFF",
        "Dracula": "#282a36",
    }

    def _tmpl_default_bg_light(self, tmpl_name: str | None = None) -> str | None:
        name = tmpl_name or (self._tmpl_cfg.get("name", "") if self._tmpl_cfg else "")
        return self._TEMPLATE_BG_LIGHT.get(name)

    def _tmpl_default_bg_dark(self, tmpl_name: str | None = None) -> str | None:
        name = tmpl_name or (self._tmpl_cfg.get("name", "") if self._tmpl_cfg else "")
        return self._TEMPLATE_BG_DARK.get(name)

    def _template_default_card_bg(self, tmpl_name: str | None = None) -> str | None:
        return self._tmpl_default_bg_dark(tmpl_name) if _is_night_mode() else self._tmpl_default_bg_light(tmpl_name)

    def _card_bg_matches_template_default(self, tmpl_name: str | None = None) -> bool:
        default_bg = self._template_default_card_bg(tmpl_name)
        if not self._card_bg_color or not default_bg:
            return False
        return (
            self._card_bg_color.lower() == default_bg.lower()
            and abs(self._card_bg_opacity - self._DEFAULT_CARD_BG_OPACITY) <= 1e-6
        )

    def _apply_template_default_card_bg(self, *, save_state: bool = True, refresh_preview: bool = True):
        self._card_bg_color = self._tmpl_default_bg_light()
        self._card_bg_opacity = self._DEFAULT_CARD_BG_OPACITY
        self._card_bg_is_custom = False
        self._card_bg_dark_color = self._tmpl_default_bg_dark()
        self._card_bg_dark_opacity = self._DEFAULT_CARD_BG_OPACITY
        self._card_bg_dark_is_custom = False
        self._save_current_template_card_bg_state()
        pct = int(self._DEFAULT_CARD_BG_OPACITY * 100)
        self._card_bg_slider.blockSignals(True)
        self._card_bg_slider.setValue(pct)
        self._card_bg_slider.blockSignals(False)
        self._card_bg_pct.setText(f"{pct}%")
        self._refresh_card_bg_btn()
        if save_state:
            self._save_note_state()
        if refresh_preview:
            self._refresh_preview()

    def _refresh_card_bg_btn(self):
        is_dark = _is_night_mode()
        color   = self._card_bg_dark_color if is_dark else self._card_bg_color
        opacity = self._card_bg_dark_opacity if is_dark else self._card_bg_opacity
        if color:
            c    = QColor(color)
            alpha = int(opacity * 255)
            rgba  = f"rgba({c.red()},{c.green()},{c.blue()},{alpha})"
            self._card_bg_btn.setStyleSheet(
                f"QPushButton {{ background-color: {rgba}; border: 1px solid {UI_BORDER}; border-radius: 4px; }}"
                f"QPushButton:hover {{ border-color: {UI_BORDER_STRONG}; }}"
            )
            self._card_bg_btn.setText("")
            self._card_bg_btn.setToolTip(f"Card BG: {color}  {int(opacity * 100)}%")
        else:
            self._card_bg_btn.setStyleSheet(
                f"QPushButton {{ background: transparent; border: 2px dashed {UI_BORDER_STRONG};"
                f" border-radius: 4px; color: {UI_TEXT_MUTED}; font-size: 12px; }}"
                f"QPushButton:hover {{ border-color: {UI_ACCENT}; }}"
            )
            self._card_bg_btn.setText("∅")
            self._card_bg_btn.setToolTip("No custom card background")

    def _pick_card_bg(self):
        is_dark = _is_night_mode()
        current = self._card_bg_dark_color if is_dark else self._card_bg_color
        start   = QColor(current) if current else QColor(Qt.GlobalColor.black if is_dark else Qt.GlobalColor.white)
        dlg     = QColorDialog(start, self)
        dlg.setWindowTitle("Card Background Color")
        dlg.setOption(QColorDialog.ColorDialogOption.DontUseNativeDialog, True)

        for box in dlg.findChildren(QDialogButtonBox):
            ok = box.button(QDialogButtonBox.StandardButton.Ok)
            if ok:
                ok.setText("Save")

        def _live(c: QColor):
            if is_dark:
                self._card_bg_dark_color    = c.name()
                self._card_bg_dark_is_custom = True
            else:
                self._card_bg_color    = c.name()
                self._card_bg_is_custom = True
            self._save_current_template_card_bg_state()
            self._refresh_card_bg_btn()
            self._save_note_state()
            self._refresh_preview()

        dlg.currentColorChanged.connect(_live)
        _position_before_preview(dlg, self)

        if dlg.exec() != QDialog.DialogCode.Accepted:
            return

        if is_dark:
            self._card_bg_dark_color    = dlg.currentColor().name()
            self._card_bg_dark_is_custom = True
        else:
            self._card_bg_color    = dlg.currentColor().name()
            self._card_bg_is_custom = True
        self._save_current_template_card_bg_state()
        self._refresh_card_bg_btn()
        self._save_note_state()
        self._refresh_preview()

    def _on_card_bg_opacity(self, val: int):
        if _is_night_mode():
            self._card_bg_dark_opacity   = val / 100.0
            self._card_bg_dark_is_custom = True
        else:
            self._card_bg_opacity   = val / 100.0
            self._card_bg_is_custom = True
        self._save_current_template_card_bg_state()
        self._card_bg_pct.setText(f"{val}%")
        self._refresh_card_bg_btn()
        self._save_note_state()
        self._refresh_preview()

    def _reset_card_bg(self):
        self._apply_template_default_card_bg(save_state=True, refresh_preview=True)

    def _card_bg_dark_rgba(self) -> str | None:
        if self._card_bg_dark_color:
            return _hex_to_rgba(self._card_bg_dark_color, self._card_bg_dark_opacity)
        return None

    # ── HR Style helpers ────────────────────────────────────────────────────────

    _HR_PRESET_LABELS = {
        "default":   "Default",
        "thin":      "Thin",
        "fade":      "Fade",
        "dashed":    "Dashed",
        "thick":     "Thick",
        "invisible": "Invisible",
        "custom":    "Custom",
    }

    def _refresh_hr_btn(self):
        if not hasattr(self, "_hr_style_btn"):
            return
        preset = (self._hr_style or {}).get("preset", "default")
        label  = self._HR_PRESET_LABELS.get(preset, "Default")
        active = preset != "default"
        border = UI_ACCENT if active else UI_BORDER
        self._hr_style_btn.setText(label)
        self._hr_style_btn.setStyleSheet(
            "QPushButton {"
            f" font-size: 10px; padding: 0 10px; height: 22px;"
            f" border: 1px solid {border}; border-radius: 3px;"
            f" background: {UI_BG_CARD}; color: {UI_TEXT};"
            "}"
            f"QPushButton:hover {{ background: {UI_BG_HOVER}; border-color: {UI_ACCENT}; }}"
        )

    def _load_hr_style(self):
        if not self._tmpl_cfg:
            self._hr_style = None
            return
        tmpl_name = self._tmpl_cfg.get("name", "")
        saved = self._read_addon_cfg().get("hr_styles", {}).get(tmpl_name)
        self._hr_style = saved if isinstance(saved, dict) else None

    def _save_hr_style(self):
        if not self._tmpl_cfg:
            return
        tmpl_name = self._tmpl_cfg.get("name", "")
        cfg       = self._read_addon_cfg()
        hr_styles = cfg.get("hr_styles", {})
        preset    = (self._hr_style or {}).get("preset", "default")
        if self._hr_style and preset != "default":
            hr_styles[tmpl_name] = self._hr_style
        else:
            hr_styles.pop(tmpl_name, None)
        cfg["hr_styles"] = hr_styles
        self._write_addon_cfg(cfg)

    def _edit_hr_style(self):
        from aqt.qt import QFormLayout
        orig_style = dict(self._hr_style) if self._hr_style else {}
        _preset    = [orig_style.get("preset", "default")]

        dlg = QDialog(self)
        dlg.setWindowTitle("Divider Style")
        dlg.setMinimumWidth(310)
        vl = QVBoxLayout(dlg)
        vl.setContentsMargins(12, 12, 12, 8)
        vl.setSpacing(8)

        tabs = QTabWidget()

        # ── Presets tab ──────────────────────────────────────────────────────
        presets_w = QWidget()
        grid      = QGridLayout(presets_w)
        grid.setSpacing(8)
        grid.setContentsMargins(8, 8, 8, 8)

        _cards      = {}
        _PRESET_INFO = [
            ("default",   "Default"),
            ("thin",      "Thin"),
            ("fade",      "Fade"),
            ("dashed",    "Dashed"),
            ("thick",     "Thick"),
            ("invisible", "Invisible"),
        ]

        def _on_preset_clicked(key):
            _preset[0] = key
            for k, c in _cards.items():
                c.set_selected(k == key)
            if key not in ("default", "invisible"):
                _fill_custom(key, block=True)
            _apply_preview()

        for i, (key, label) in enumerate(_PRESET_INFO):
            card = _PresetCard(key, label, self._dark, _on_preset_clicked)
            card.set_selected(key == _preset[0])
            _cards[key] = card
            grid.addWidget(card, i // 2, i % 2)

        tabs.addTab(presets_w, "Presets")

        # ── Custom tab ───────────────────────────────────────────────────────
        custom_w = QWidget()
        form     = QFormLayout(custom_w)
        form.setSpacing(8)
        form.setContentsMargins(10, 10, 10, 8)

        color_combo = QComboBox()
        for t_key, t_lbl in [("border", "Border"), ("muted", "Muted"), ("accent", "Accent"), ("text", "Text")]:
            color_combo.addItem(t_lbl, t_key)
        form.addRow("Color:", color_combo)

        thickness_spin = QSpinBox()
        thickness_spin.setRange(1, 10)
        form.addRow("Thickness:", thickness_spin)

        line_style_combo = QComboBox()
        for s_key, s_lbl in [("solid", "Solid"), ("dashed", "Dashed"), ("dotted", "Dotted")]:
            line_style_combo.addItem(s_lbl, s_key)
        form.addRow("Style:", line_style_combo)

        width_row = QWidget()
        width_hl  = QHBoxLayout(width_row)
        width_hl.setContentsMargins(0, 0, 0, 0)
        width_hl.setSpacing(6)
        width_slider = QSlider(Qt.Orientation.Horizontal)
        width_slider.setRange(20, 100)
        width_slider.setFixedWidth(100)
        width_pct_lbl = QLabel("100%")
        width_pct_lbl.setFixedWidth(34)
        width_pct_lbl.setStyleSheet(f"font-size: 11px; color: {UI_TEXT};")
        width_slider.valueChanged.connect(lambda v: width_pct_lbl.setText(f"{v}%"))
        width_hl.addWidget(width_slider)
        width_hl.addWidget(width_pct_lbl)
        width_hl.addStretch()
        form.addRow("Width:", width_row)

        margin_top_spin = QSpinBox()
        margin_top_spin.setRange(-50, 200)
        form.addRow("Margin top:", margin_top_spin)

        margin_bot_spin = QSpinBox()
        margin_bot_spin.setRange(-50, 200)
        form.addRow("Margin bottom:", margin_bot_spin)

        tabs.addTab(custom_w, "Custom")
        vl.addWidget(tabs)

        # ── Helpers ──────────────────────────────────────────────────────────
        def _get_custom_cfg() -> dict:
            return {
                "preset":        "custom",
                "color_token":   color_combo.currentData(),
                "thickness":     thickness_spin.value(),
                "style":         line_style_combo.currentData(),
                "width_pct":     width_slider.value(),
                "margin_top":    margin_top_spin.value(),
                "margin_bottom": margin_bot_spin.value(),
            }

        def _fill_custom(key: str, block: bool = False):
            if key in HR_PRESETS:
                cfg = HR_PRESETS[key]
            elif key == "custom" and orig_style.get("preset") == "custom":
                cfg = orig_style
            else:
                cfg = {}

            pairs = [
                (color_combo,       "color_token",  "border"),
                (thickness_spin,    "thickness",    1),
                (line_style_combo,  "style",        "solid"),
                (width_slider,      "width_pct",    100),
                (margin_top_spin,   "margin_top",   12),
                (margin_bot_spin,   "margin_bottom", 12),
            ]
            for ctrl, field, default in pairs:
                val = cfg.get(field, default)
                if block:
                    ctrl.blockSignals(True)
                if isinstance(ctrl, QComboBox):
                    idx = ctrl.findData(val)
                    if idx >= 0:
                        ctrl.setCurrentIndex(idx)
                else:
                    ctrl.setValue(val)
                if block:
                    ctrl.blockSignals(False)
            width_pct_lbl.setText(f"{cfg.get('width_pct', 100)}%")

        def _apply_preview():
            p = _preset[0]
            if p == "default":
                self._hr_style = None
            elif p == "invisible":
                self._hr_style = {"preset": "invisible"}
            elif p == "custom":
                self._hr_style = _get_custom_cfg()
            else:
                self._hr_style = {"preset": p}
            self._refresh_hr_btn()
            self._refresh_preview()

        def _on_custom_changed(_=None):
            _preset[0] = "custom"
            for c in _cards.values():
                c.set_selected(False)
            _apply_preview()

        for ctrl in (color_combo, thickness_spin, line_style_combo,
                     width_slider, margin_top_spin, margin_bot_spin):
            if isinstance(ctrl, QComboBox):
                ctrl.currentIndexChanged.connect(_on_custom_changed)
            else:
                ctrl.valueChanged.connect(_on_custom_changed)

        # Initialize controls from saved state
        cur = _preset[0]
        if cur == "custom":
            _fill_custom("custom", block=True)
        elif cur not in ("default", "invisible"):
            _fill_custom(cur, block=True)
        else:
            _fill_custom("thin", block=True)

        # ── Save / Cancel ─────────────────────────────────────────────────────
        btns       = QDialogButtonBox()
        save_btn   = btns.addButton("Save",   QDialogButtonBox.ButtonRole.AcceptRole)
        cancel_btn = btns.addButton(QDialogButtonBox.StandardButton.Cancel)
        save_btn.clicked.connect(dlg.accept)
        cancel_btn.clicked.connect(dlg.reject)
        vl.addWidget(btns)

        if dlg.exec() == QDialog.DialogCode.Accepted:
            _apply_preview()
            self._save_hr_style()
        else:
            self._hr_style = dict(orig_style) if orig_style else None
            self._refresh_hr_btn()
            self._refresh_preview()

    def _make_col_header(self) -> QWidget:
        w = QWidget()
        hl = QHBoxLayout(w)
        hl.setContentsMargins(4, 0, 8, 0)  # mirrors FieldRowWidget margins exactly
        hl.setSpacing(6)                    # mirrors FieldRowWidget spacing exactly

        handle_ph = QWidget()
        handle_ph.setFixedWidth(20)
        hl.addWidget(handle_ph)

        name_ph = QWidget()
        name_ph.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        hl.addWidget(name_ph)

        def _lbl(text: str, width: int) -> QLabel:
            lb = QLabel(text)
            lb.setFixedWidth(width)
            lb.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lb.setStyleSheet(f"font-size: 10px; font-weight: 600; color: {UI_TEXT_MUTED};")
            return lb

        hl.addWidget(_lbl("Color",   30))
        hl.addWidget(_lbl("Font",    FieldRowWidget.FONT_W))
        hl.addWidget(_lbl("Align",   FieldRowWidget.ALIGN_W))
        hl.addWidget(_lbl("Size",    FieldRowWidget.SPIN_W))
        hl.addWidget(_lbl("Spacing", FieldRowWidget.SPACING_BTN_W))
        return w

    def _build_mapping_section(self) -> QGroupBox:
        box = self._make_group("Field Mapping")
        vbox = QVBoxLayout(box)
        vbox.setContentsMargins(10, 14, 10, 10)
        vbox.setSpacing(6)

        hint = QLabel("Drag fields between Front and Back. Click color, align, font, or size to edit.")
        hint.setWordWrap(True)
        hint.setStyleSheet(f"color: {UI_TEXT_MUTED}; font-size: 10px;")
        vbox.addWidget(hint)

        naming_hint = QLabel("⚠ Fields for audio must be named <b>audio</b> or <b>sound</b>, and for images <b>img</b> or <b>image</b> — otherwise media styling won't apply.")
        naming_hint.setWordWrap(True)
        naming_hint.setStyleSheet("color: #c8922a; font-size: 10px; margin-top: 2px;")
        vbox.addWidget(naming_hint)

        vbox.addWidget(self._make_col_header())

        front_lbl = QLabel("Front")
        front_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {UI_TEXT};")
        vbox.addWidget(front_lbl)

        self.front_list = FieldListWidget()
        self.front_list._is_mapping_list = True
        self.front_list._role = "front"
        self.front_list.on_changed = self._on_fields_changed
        self.front_list.on_virtual_drop = self._on_virtual_drop
        vbox.addWidget(self.front_list)

        back_lbl = QLabel("Back")
        back_lbl.setStyleSheet(f"font-weight: bold; font-size: 11px; color: {UI_TEXT}; margin-top: 4px;")
        vbox.addWidget(back_lbl)

        self.back_list = FieldListWidget()
        self.back_list._is_mapping_list = True
        self.back_list._role = "back"
        self.back_list.on_changed = self._on_fields_changed
        self.back_list.on_virtual_drop = self._on_virtual_drop
        vbox.addWidget(self.back_list)

        unmapped_header = QWidget()
        unmapped_header.setStyleSheet("margin-top: 4px;")
        unmapped_hl = QHBoxLayout(unmapped_header)
        unmapped_hl.setContentsMargins(0, 0, 0, 0)
        unmapped_hl.setSpacing(4)

        self._unmapped_toggle = QPushButton("▶  Unmapped")
        self._unmapped_toggle.setCheckable(True)
        self._unmapped_toggle.setChecked(False)
        self._unmapped_toggle.setStyleSheet(
            "QPushButton {"
            f" font-weight: bold; font-size: 11px; color: {UI_TEXT_MUTED};"
            " background: transparent; border: none; padding: 0; text-align: left;"
            "}"
            "QPushButton:hover {"
            f" color: {UI_TEXT};"
            "}"
        )
        self._unmapped_toggle.clicked.connect(self._toggle_unmapped)
        unmapped_hl.addWidget(self._unmapped_toggle)
        unmapped_hl.addStretch()
        vbox.addWidget(unmapped_header)

        self._unmapped_hint = QLabel("Fields not used in this card template. Drag to Front or Back to include.")
        self._unmapped_hint.setWordWrap(True)
        self._unmapped_hint.setStyleSheet(f"color: {UI_TEXT_MUTED}; font-size: 10px;")
        self._unmapped_hint.setVisible(False)
        vbox.addWidget(self._unmapped_hint)

        self.unmapped_list = FieldListWidget()
        self.unmapped_list._role = "unmapped"
        self.unmapped_list.on_changed = self._on_fields_changed
        self.unmapped_list.setVisible(False)
        vbox.addWidget(self.unmapped_list)

        return box

    def _build_action_buttons(self) -> QWidget:
        w = QWidget()
        hl = QHBoxLayout(w)
        hl.setContentsMargins(0, 4, 0, 4)

        backup_btn = QPushButton("Backup")
        backup_btn.clicked.connect(self._do_backup)

        restore_btn = QPushButton("Restore...")
        restore_btn.clicked.connect(self._do_restore)

        reset_btn = QPushButton("Reset to defaults")
        reset_btn.clicked.connect(self._do_reset_to_defaults)

        apply_btn = QPushButton("Apply Template")
        apply_btn.setStyleSheet(
            "QPushButton {"
            " background: #0078d4; color: white; font-weight: bold;"
            " padding: 7px 16px; border-radius: 4px; border: none;"
            "}"
            "QPushButton:hover   { background: #106ebe; }"
            "QPushButton:pressed { background: #005a9e; }"
        )
        apply_btn.clicked.connect(self._do_apply)

        hl.addWidget(backup_btn)
        hl.addWidget(restore_btn)
        hl.addWidget(reset_btn)
        hl.addStretch()
        hl.addWidget(apply_btn)
        return w

    # ── Data Loading ───────────────────────────────────────────────────────────

    def _load_note_types(self):
        self.note_type_combo.blockSignals(True)
        self.note_type_combo.clear()
        self._note_types = get_note_types()
        for m in self._note_types:
            self.note_type_combo.addItem(m["name"])
        initial_idx = 0
        if self._initial_note_type:
            for i, m in enumerate(self._note_types):
                if m["name"] == self._initial_note_type:
                    initial_idx = i
                    break
        self.note_type_combo.setCurrentIndex(initial_idx)
        self.note_type_combo.blockSignals(False)
        if self._note_types:
            self._on_note_type_changed(initial_idx)

    def _load_prettify_templates(self):
        self._prettify_templates = get_all_templates()
        self.prettify_combo.blockSignals(True)
        for t in self._prettify_templates:
            self.prettify_combo.addItem(t["name"])
        self.prettify_combo.blockSignals(False)
        if self._prettify_templates:
            self._on_prettify_changed(0)

    # ── Event Handlers ─────────────────────────────────────────────────────────

    def _on_note_type_changed(self, idx: int):
        if idx < 0 or idx >= len(self._note_types):
            return
        self._note_model = self._note_types[idx]
        fields     = get_fields(self._note_model)
        self._note_type_fields = fields
        card_tmpls = get_card_templates(self._note_model)

        self._loading_note_type = True
        self.card_tmpl_combo.blockSignals(True)
        self.card_tmpl_combo.clear()
        for t in card_tmpls:
            self.card_tmpl_combo.addItem(t["name"])
        self.card_tmpl_combo.blockSignals(False)
        initial_tmpl_idx = 0
        if hasattr(self, '_initial_card_tmpl_ord') and self._initial_card_tmpl_ord:
            for i, t in enumerate(card_tmpls):
                if t.get("ord") == self._initial_card_tmpl_ord:
                    initial_tmpl_idx = i
                    break
        self._initial_card_tmpl_ord = 0
        self.card_tmpl_combo.setCurrentIndex(initial_tmpl_idx)
        self._on_card_tmpl_changed(initial_tmpl_idx)
        self._loading_note_type = False

        if not self._try_restore_note_state(fields):
            if self._card_tmpl:
                self._auto_map_fields_from_template(fields)
                self._apply_sibling_field_styles()
            else:
                self._reset_field_lists(fields)
        self._refresh_preview()

    def _on_card_tmpl_changed(self, idx: int):
        tmpls = get_card_templates(self._note_model) if self._note_model else []
        self._card_tmpl = tmpls[idx] if 0 <= idx < len(tmpls) else None
        if getattr(self, '_loading_note_type', False) or not self._note_model or not self._card_tmpl:
            return
        fields = get_fields(self._note_model)
        self._note_type_fields = fields
        if not self._restore_card_fields_from_state(fields):
            self._auto_map_fields_from_template(fields)
        self._apply_sibling_field_styles()
        self._save_note_state()
        self._refresh_preview()

    def _on_prettify_changed(self, idx: int):
        if idx < 0 or idx >= len(self._prettify_templates):
            return
        self._save_current_template_card_bg_state()
        self._tmpl_cfg = self._prettify_templates[idx]
        self.tmpl_desc.setText(self._tmpl_cfg.get("description", ""))
        self._load_current_template_card_bg_state()
        self._load_hr_style()
        self._refresh_hr_btn()
        if self._note_model:
            self._recolor_field_lists()
        self._save_note_state()
        self._refresh_preview()

    def _toggle_unmapped(self) -> None:
        expanded = self._unmapped_toggle.isChecked()
        self._unmapped_toggle.setText("▼  Unmapped" if expanded else "▶  Unmapped")
        self._unmapped_hint.setVisible(expanded)
        self.unmapped_list.setVisible(expanded)

    def _on_fields_changed(self) -> None:
        self._sync_fields_from_lists()
        self._save_note_state()
        self._refresh_preview()

    def _on_virtual_drop(self, field: dict) -> dict | None:
        available = [f for f in self._note_type_fields if f]
        dlg = TypeAnswerFieldDialog(self, available, field.get("compare_field", ""))
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return None
        updated = dict(field)
        updated["compare_field"] = dlg.selected_field()
        return updated

    # ── Field List Management ──────────────────────────────────────────────────

    def _make_field_dict(self, name: str, *, is_front: bool, index: int) -> dict:
        key = self._field_default_key(name, is_front=is_front, index=index)
        style = self._get_default_style(key)
        is_audio = is_audio_field(name)
        is_image = is_image_field(name)
        t_color        = self._default_field_color(name, is_front=is_front, list_idx=index)
        t_font_size    = style.get("font_size", 16 if is_front else 14)
        t_media_width  = style.get("media_width", 280 if is_audio else 200 if is_image else None)
        t_media_height = style.get("media_height", 32 if is_audio else 200 if is_image else None)
        return {
            "name":          name,
            "color":         t_color,
            "font_size":     t_font_size,
            "media_width":   t_media_width,
            "media_height":  t_media_height,
            "align":         "center",
            "padding_v":     0,
            "padding_h":     0,
            "margin_top":    0,
            "margin_bottom": 0,
            "line_height":   1.5,
            "_template_defaults": {
                "color":        t_color,
                "font_size":    t_font_size,
                "media_width":  t_media_width,
                "media_height": t_media_height,
            },
        }

    def _inject_template_defaults(self, field: dict, *, is_front: bool, idx: int) -> None:
        if field.get("virtual") or "_template_defaults" in field:
            return
        name = field.get("name", "")
        key = self._field_default_key(name, is_front=is_front, index=idx)
        style = self._get_default_style(key)
        is_audio = is_audio_field(name)
        is_image = is_image_field(name)
        field["_template_defaults"] = {
            "color":        self._default_field_color(name, is_front=is_front, list_idx=idx),
            "font_size":    style.get("font_size", 16 if is_front else 14),
            "media_width":  style.get("media_width", 280 if is_audio else 200 if is_image else None),
            "media_height": style.get("media_height", 32 if is_audio else 200 if is_image else None),
        }

    def _auto_map_fields_from_template(self, fields: list[str]) -> None:
        """First-time mapping: distribute fields based on the current card template."""
        self.front_list.on_changed   = None
        self.back_list.on_changed    = None
        self.unmapped_list.on_changed = None
        self.front_list.clear()
        self.back_list.clear()
        self.unmapped_list.clear()

        known = set(fields)
        card = self._card_tmpl or {}
        front_names = parse_template_fields(card.get("qfmt", ""), known)
        back_names  = parse_template_fields(card.get("afmt", ""), known)
        front_set   = set(front_names)
        back_set    = set(back_names)

        for i, name in enumerate(front_names):
            self.front_list.add_field(self._make_field_dict(name, is_front=True, index=i))

        back_only_idx = 0
        for name in back_names:
            if name not in front_set:
                self.back_list.add_field(self._make_field_dict(name, is_front=False, index=back_only_idx))
                back_only_idx += 1

        # Fields present in the note type but referenced by neither template side.
        self.unmapped_list.add_field({"name": _TYPE_ANSWER_BOX, "virtual": True, "compare_field": ""})
        unmapped_idx = 0
        for name in fields:
            if name not in front_set and name not in back_set:
                self.unmapped_list.add_field(
                    self._make_field_dict(name, is_front=False, index=unmapped_idx)
                )
                unmapped_idx += 1

        self._sync_fields_from_lists()
        self.front_list.on_changed   = self._on_fields_changed
        self.back_list.on_changed    = self._on_fields_changed
        self.unmapped_list.on_changed = self._on_fields_changed

    def _reset_field_lists(self, fields: list[str]) -> None:
        """Fallback mapping when no template is available: first field → Front, rest → Back."""
        self.front_list.on_changed   = None
        self.back_list.on_changed    = None
        self.unmapped_list.on_changed = None
        self.front_list.clear()
        self.back_list.clear()
        self.unmapped_list.clear()

        self.unmapped_list.add_field({"name": _TYPE_ANSWER_BOX, "virtual": True, "compare_field": ""})
        for i, name in enumerate(fields):
            is_front = i == 0
            d = self._make_field_dict(name, is_front=is_front, index=i)
            if is_front:
                self.front_list.add_field(d)
            else:
                self.back_list.add_field(d)

        self._sync_fields_from_lists()
        self.front_list.on_changed   = self._on_fields_changed
        self.back_list.on_changed    = self._on_fields_changed
        self.unmapped_list.on_changed = self._on_fields_changed

    def _save_note_state(self) -> None:
        if not self._note_model or getattr(self, '_restoring_note_state', False):
            return
        cfg = self._read_addon_cfg()
        note_states = cfg.get("note_states", {})
        lh = self._line_height_spin.value() if hasattr(self, "_line_height_spin") else 1.0
        fg = self._field_gap_spin.value() if hasattr(self, "_field_gap_spin") else -1
        self._save_current_template_card_bg_state()
        def _strip_meta(fields: list) -> list:
            return [{k: v for k, v in f.items() if not k.startswith("_")} for f in fields]

        note_key = self._note_model["name"]
        card_key = self._card_tmpl.get("name", "") if self._card_tmpl else ""
        per_note = note_states.get(note_key, {})
        if "prettify_template" in per_note or "front_fields" in per_note:
            per_note = {}  # discard legacy flat structure
        per_note["_global"] = {
            "prettify_template": self._tmpl_cfg.get("name", "") if self._tmpl_cfg else "",
            "line_height":       lh,
            "field_gap":         fg,
            "card_bg_color":     self._card_bg_color,
            "card_bg_opacity":   self._card_bg_opacity,
            "card_bg_is_custom": self._card_bg_is_custom,
            "card_bg_by_template": self._card_bg_by_template,
        }
        per_note[card_key] = {
            "front_fields":    _strip_meta(self.front_list.get_fields()    if hasattr(self, "front_list")    else []),
            "back_fields":     _strip_meta(self.back_list.get_fields()     if hasattr(self, "back_list")     else []),
            "unmapped_fields": _strip_meta(self.unmapped_list.get_fields() if hasattr(self, "unmapped_list") else []),
        }
        _STYLE_KEYS = {
            "color", "font_size", "font_family", "font_weight", "font_italic",
            "align", "padding_v", "padding_h", "margin_top", "margin_bottom",
            "media_width", "media_height", "audio_icon_color", "audio_bg_color", "audio_hidden",
        }
        all_cur = (per_note[card_key]["front_fields"]
                   + per_note[card_key]["back_fields"]
                   + per_note[card_key].get("unmapped_fields", []))
        style_by_name = {
            f["name"]: {k: v for k, v in f.items() if k in _STYLE_KEYS}
            for f in all_cur if "name" in f
        }
        for other_key, other_state in per_note.items():
            if other_key in ("_global", card_key) or not isinstance(other_state, dict):
                continue
            for section in ("front_fields", "back_fields", "unmapped_fields"):
                for field in other_state.get(section, []):
                    if field.get("name") in style_by_name:
                        field.update(style_by_name[field["name"]])
        note_states[note_key] = per_note
        cfg["note_states"] = note_states
        self._write_addon_cfg(cfg)

    def _apply_sibling_field_styles(self) -> None:
        if not self._note_model or not self._card_tmpl:
            return
        note_key = self._note_model["name"]
        current_card_key = self._card_tmpl.get("name", "")
        cfg = self._read_addon_cfg()
        _STYLE_KEYS = {
            "color", "font_size", "font_family", "font_weight", "font_italic",
            "align", "padding_v", "padding_h", "margin_top", "margin_bottom",
            "media_width", "media_height", "audio_icon_color", "audio_bg_color", "audio_hidden",
        }
        style_by_name: dict[str, dict] = {}
        for src_key in ("note_states", "applied_note_states"):
            per_note = cfg.get(src_key, {}).get(note_key, {})
            for card_key, card_state in per_note.items():
                if card_key in ("_global", current_card_key) or not isinstance(card_state, dict):
                    continue
                for section in ("front_fields", "back_fields", "unmapped_fields"):
                    for f in card_state.get(section, []):
                        name = f.get("name")
                        if name and name not in style_by_name:
                            styles = {k: v for k, v in f.items() if k in _STYLE_KEYS}
                            if styles:
                                style_by_name[name] = styles
        if not style_by_name:
            return
        for lst in (self.front_list, self.back_list, self.unmapped_list):
            for row in lst._rows:
                name = row._field.get("name")
                if name in style_by_name:
                    row.apply_styles(style_by_name[name])

    def _save_current_template_card_bg_state(self) -> None:
        tmpl_name = self._tmpl_cfg.get("name", "") if self._tmpl_cfg else ""
        if not tmpl_name:
            return
        self._card_bg_by_template[tmpl_name] = {
            "color":          self._card_bg_color,
            "opacity":        self._card_bg_opacity,
            "is_custom":      self._card_bg_is_custom,
            "dark_color":     self._card_bg_dark_color,
            "dark_opacity":   self._card_bg_dark_opacity,
            "dark_is_custom": self._card_bg_dark_is_custom,
        }

    def _load_current_template_card_bg_state(self) -> None:
        tmpl_name = self._tmpl_cfg.get("name", "") if self._tmpl_cfg else ""
        if not tmpl_name:
            return
        state = self._card_bg_by_template.get(tmpl_name)
        if isinstance(state, dict):
            self._card_bg_color = state.get("color")
            self._card_bg_opacity = state.get("opacity", self._DEFAULT_CARD_BG_OPACITY)
            self._card_bg_is_custom = bool(state.get("is_custom", False))
            if not self._card_bg_is_custom:
                self._card_bg_color = self._tmpl_default_bg_light(tmpl_name)
                self._card_bg_opacity = self._DEFAULT_CARD_BG_OPACITY
            self._card_bg_dark_color = state.get("dark_color")
            self._card_bg_dark_opacity = state.get("dark_opacity", self._DEFAULT_CARD_BG_OPACITY)
            self._card_bg_dark_is_custom = bool(state.get("dark_is_custom", False))
            if not self._card_bg_dark_is_custom:
                self._card_bg_dark_color = self._tmpl_default_bg_dark(tmpl_name)
                self._card_bg_dark_opacity = self._DEFAULT_CARD_BG_OPACITY
        else:
            self._card_bg_color = self._tmpl_default_bg_light(tmpl_name)
            self._card_bg_opacity = self._DEFAULT_CARD_BG_OPACITY
            self._card_bg_is_custom = False
            self._card_bg_dark_color = self._tmpl_default_bg_dark(tmpl_name)
            self._card_bg_dark_opacity = self._DEFAULT_CARD_BG_OPACITY
            self._card_bg_dark_is_custom = False
            self._save_current_template_card_bg_state()
        if hasattr(self, "_card_bg_slider"):
            is_dark = _is_night_mode()
            opacity = self._card_bg_dark_opacity if is_dark else self._card_bg_opacity
            self._card_bg_slider.blockSignals(True)
            self._card_bg_slider.setValue(int(opacity * 100))
            self._card_bg_slider.blockSignals(False)
        if hasattr(self, "_card_bg_pct"):
            is_dark = _is_night_mode()
            opacity = self._card_bg_dark_opacity if is_dark else self._card_bg_opacity
            self._card_bg_pct.setText(f"{int(opacity * 100)}%")
        if hasattr(self, "_card_bg_btn"):
            self._refresh_card_bg_btn()

    def _try_restore_note_state(self, current_fields: list[str]) -> bool:
        """Restore saved state for the current note type. Returns True if restored."""
        if not self._note_model:
            return False
        card_key     = self._card_tmpl.get("name", "") if self._card_tmpl else ""
        note_applied = self._read_addon_cfg().get("applied_note_states", {}).get(self._note_model["name"], {})
        if "prettify_template" in note_applied or "front_fields" in note_applied:
            return False  # legacy flat structure — discard, auto-map instead

        global_state = note_applied.get("_global")
        card_state   = note_applied.get(card_key)

        # Old-format migration: per-card entries had all settings incl. prettify_template
        if global_state is None and note_applied:
            for val in note_applied.values():
                if isinstance(val, dict) and "prettify_template" in val:
                    global_state = val
                    break

        if global_state is None and card_state is None:
            return False

        self._restoring_note_state = True
        src = global_state or {}

        # Restore prettify template (global)
        tmpl_name = src.get("prettify_template", "")
        if tmpl_name:
            for i, t in enumerate(self._prettify_templates):
                if t["name"] == tmpl_name:
                    self.prettify_combo.blockSignals(True)
                    self.prettify_combo.setCurrentIndex(i)
                    self.prettify_combo.blockSignals(False)
                    self._tmpl_cfg = self._prettify_templates[i]
                    self.tmpl_desc.setText(self._tmpl_cfg.get("description", ""))
                    self._load_hr_style()
                    self._refresh_hr_btn()
                    break

        # Restore line height (global)
        if hasattr(self, "_line_height_spin"):
            self._line_height_spin.setValue(src.get("line_height", 1.0))

        # Restore field gap (global)
        if hasattr(self, "_field_gap_spin"):
            self._field_gap_spin.setValue(src.get("field_gap", -1))

        # Restore card BG (global)
        raw_map = src.get("card_bg_by_template")
        self._card_bg_by_template = raw_map if isinstance(raw_map, dict) else {}
        legacy_color   = src.get("card_bg_color")
        legacy_opacity = src.get("card_bg_opacity", self._DEFAULT_CARD_BG_OPACITY)
        legacy_custom  = src.get("card_bg_is_custom")
        selected_tmpl_name = self._tmpl_cfg.get("name", "") if self._tmpl_cfg else ""
        if selected_tmpl_name and selected_tmpl_name not in self._card_bg_by_template and legacy_color is not None:
            if legacy_custom is None:
                default_bg = self._template_default_card_bg(selected_tmpl_name)
                legacy_is_custom = (
                    bool(legacy_color)
                    and (
                        str(legacy_color).lower() != (default_bg or "").lower()
                        or abs(legacy_opacity - 1.0) > 1e-6
                    )
                )
            else:
                legacy_is_custom = bool(legacy_custom)
            self._card_bg_by_template[selected_tmpl_name] = {
                "color":     legacy_color,
                "opacity":   legacy_opacity,
                "is_custom": legacy_is_custom,
            }
        self._load_current_template_card_bg_state()

        # Restore per-card field lists
        if card_state and "front_fields" in card_state:
            fields_src = card_state
        elif src.get("front_fields"):  # old format: global_state carried field data
            fields_src = src
        else:
            # Global settings restored but no per-card field data; let caller auto-map.
            self._restoring_note_state = False
            return False

        self._restore_field_lists(fields_src, current_fields)
        self._restoring_note_state = False
        return True

    def _restore_field_lists(self, state: dict, current_fields: list[str]) -> None:
        current_field_set = set(current_fields)
        saved_front    = [f for f in state.get("front_fields",    []) if f.get("virtual") or f.get("name") in current_field_set]
        saved_back     = [f for f in state.get("back_fields",     []) if f.get("virtual") or f.get("name") in current_field_set]
        saved_unmapped = [f for f in state.get("unmapped_fields", []) if f.get("virtual") or f.get("name") in current_field_set]
        saved_names = {f["name"] for f in saved_front + saved_back + saved_unmapped}
        for i, name in enumerate(current_fields):
            if name not in saved_names:
                saved_unmapped.append(self._make_field_dict(name, is_front=False, index=i))
        has_virtual = any(f.get("virtual") for f in saved_front + saved_back + saved_unmapped)
        if not has_virtual:
            saved_unmapped.insert(0, {"name": _TYPE_ANSWER_BOX, "virtual": True, "compare_field": ""})
        for idx, f in enumerate(saved_front):
            self._inject_template_defaults(f, is_front=True, idx=idx)
        for idx, f in enumerate(saved_back, start=1):
            self._inject_template_defaults(f, is_front=False, idx=idx)
        for idx, f in enumerate(saved_unmapped):
            self._inject_template_defaults(f, is_front=False, idx=idx)
        self.front_list.on_changed    = None
        self.back_list.on_changed     = None
        self.unmapped_list.on_changed = None
        self.front_list.clear()
        self.back_list.clear()
        self.unmapped_list.clear()
        for f in saved_front:
            self.front_list.add_field(f)
        for f in saved_back:
            self.back_list.add_field(f)
        for f in saved_unmapped:
            self.unmapped_list.add_field(f)
        self._sync_fields_from_lists()
        self.front_list.on_changed    = self._on_fields_changed
        self.back_list.on_changed     = self._on_fields_changed
        self.unmapped_list.on_changed = self._on_fields_changed

    def _restore_card_fields_from_state(self, current_fields: list[str]) -> bool:
        if not self._note_model or not self._card_tmpl:
            return False
        card_key  = self._card_tmpl.get("name", "")
        note_name = self._note_model["name"]
        cfg       = self._read_addon_cfg()
        note_draft = cfg.get("note_states", {}).get(note_name, {})
        state = note_draft.get(card_key) if isinstance(note_draft.get(card_key), dict) else None
        if state is None:
            note_applied = cfg.get("applied_note_states", {}).get(note_name, {})
            state = note_applied.get(card_key) if isinstance(note_applied.get(card_key), dict) else None
        if not state or "front_fields" not in state:
            return False
        self._restore_field_lists(state, current_fields)
        return True

    def _recolor_field_lists(self) -> None:
        self.front_list.on_changed   = None
        self.back_list.on_changed    = None
        self.unmapped_list.on_changed = None

        front_fields    = self.front_list.get_fields()
        back_fields     = self.back_list.get_fields()
        unmapped_fields = self.unmapped_list.get_fields()

        def _apply(field: dict, *, is_front: bool, idx: int) -> None:
            if field.get("virtual"):
                return
            name = field.get("name", "")
            key = self._field_default_key(name, is_front=is_front, index=idx)
            style = self._get_default_style(key)
            old = field.get("_template_defaults", {})

            new_color     = self._default_field_color(name, is_front=is_front, list_idx=idx)
            new_font_size = style.get("font_size", 16 if is_front else 14)

            if field.get("color") == old.get("color"):
                field["color"] = new_color
            if field.get("font_size") == old.get("font_size"):
                field["font_size"] = new_font_size

            new_defaults = {"color": new_color, "font_size": new_font_size}

            if is_audio_field(name) or is_image_field(name):
                default_w = 280 if is_audio_field(name) else 200
                default_h = 32 if is_audio_field(name) else 200
                new_w = style.get("media_width", default_w)
                new_h = style.get("media_height", default_h)
                if field.get("media_width") == old.get("media_width"):
                    field["media_width"] = new_w
                if field.get("media_height") == old.get("media_height"):
                    field["media_height"] = new_h
                new_defaults["media_width"] = new_w
                new_defaults["media_height"] = new_h

            field["_template_defaults"] = new_defaults

        for idx, field in enumerate(front_fields):
            _apply(field, is_front=True, idx=idx)

        for idx, field in enumerate(back_fields, start=1):
            _apply(field, is_front=False, idx=idx)

        self.front_list.clear()
        self.back_list.clear()
        self.unmapped_list.clear()

        for field in front_fields:
            self.front_list.add_field(field)
        for field in back_fields:
            self.back_list.add_field(field)
        for field in unmapped_fields:
            self.unmapped_list.add_field(field)

        self.front_list.on_changed   = self._on_fields_changed
        self.back_list.on_changed    = self._on_fields_changed
        self.unmapped_list.on_changed = self._on_fields_changed
        self._sync_fields_from_lists()

    def _get_default_style(self, key: str) -> dict:
        if not self._tmpl_cfg:
            return {}
        if self._dark:
            defaults = self._tmpl_cfg.get("defaults_dark", self._tmpl_cfg.get("defaults", {}))
        else:
            defaults = self._tmpl_cfg.get("defaults_light", self._tmpl_cfg.get("defaults", {}))
        style = defaults.get(key, {})
        return style if isinstance(style, dict) else {}

    def _field_default_key(self, field_name: str, *, is_front: bool, index: int) -> str:
        if is_front or index == 0:
            return "primary"

        norm = normalize_field_name(field_name)

        if is_audio_field(field_name):
            return "audio"
        if is_image_field(field_name):
            return "image"
        if any(k in norm for k in ("extra 2", "extra2", "hint 2", "hint2", "note 2", "note2", "example 2", "example2")):
            return "extra2"
        if any(k in norm for k in ("extra 1", "extra1", "extra", "hint", "note", "example", "mnemonic")):
            return "extra1"
        return "answer"

    def _get_positional_color(self, global_index: int) -> str | None:
        if not self._tmpl_cfg:
            return None
        if self._dark:
            colors = self._tmpl_cfg.get("field_colors_dark", self._tmpl_cfg.get("field_colors"))
        else:
            colors = self._tmpl_cfg.get("field_colors_light", self._tmpl_cfg.get("field_colors"))
        if not colors or global_index >= len(colors):
            return None
        return colors[global_index]

    def _default_field_color(self, name: str, *, is_front: bool, list_idx: int) -> str:
        if not (is_audio_field(name) or is_image_field(name)):
            try:
                global_idx = self._note_type_fields.index(name)
            except ValueError:
                global_idx = list_idx
            color = self._get_positional_color(global_idx)
            if color is not None:
                return color
        key = self._field_default_key(name, is_front=is_front, index=list_idx)
        return self._get_default_style(key).get("color", "#333333")

    def _sync_fields_from_lists(self) -> None:
        self._front_fields   = self.front_list.get_fields()
        self._back_fields    = self.back_list.get_fields()
        # unmapped fields are tracked but not included in HTML/CSS generation
        front_names = {f["name"] for f in self._front_fields}
        self.back_list.refresh_dimmed(front_names)

    def _compare_style_dicts(self) -> list:
        front_back_names = {
            f["name"] for f in self._front_fields + self._back_fields
            if not f.get("virtual")
        }
        needed = {
            f.get("compare_field") for f in self._front_fields
            if f.get("virtual") and f.get("compare_field")
        }
        if not needed:
            return []
        return [
            f for f in self.unmapped_list.get_fields()
            if not f.get("virtual")
            and f.get("name") in needed
            and f.get("name") not in front_back_names
        ]

    # ── Preview ────────────────────────────────────────────────────────────────

    def _card_bg_rgba(self) -> str | None:
        if self._card_bg_color:
            return _hex_to_rgba(self._card_bg_color, self._card_bg_opacity)
        return None

    def _refresh_preview(self, _=None):
        if not self._tmpl_cfg:
            return

        self._sync_fields_from_lists()

        tab  = self.preview_tabs.currentIndex()
        side = "back" if tab == 1 else "front"
        lh   = self._line_height_spin.value() if hasattr(self, "_line_height_spin") else 1.0
        fg   = self._field_gap_spin.value() if hasattr(self, "_field_gap_spin") else -1
        css  = build_css(self._tmpl_cfg, self._front_fields, self._back_fields,
                         line_height=lh,
                         field_gap=fg if fg >= 0 else None,
                         card_bg_light=self._card_bg_rgba(),
                         card_bg_dark=self._card_bg_dark_rgba(),
                         hr_style=self._hr_style,
                         compare_field_dicts=self._compare_style_dicts())
        body = (
            build_front(self._front_fields, preview=True) if side == "front"
            else build_back(self._front_fields, self._back_fields, preview=True)
        )

        body_class = "card night_mode" if self._dark else "card"
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<style>html,body{{margin:0;padding:0;height:100%;}}{css}</style>"
            f"</head><body class='{body_class}'>{body}</body></html>"
        )

        widget = self.preview_front if side == "front" else self.preview_back
        self._set_html(widget, html)

    def _read_addon_cfg(self) -> dict:
        cfg = mw.addonManager.getConfig(ADDON_MODULE)
        return cfg if cfg else {}

    def _write_addon_cfg(self, cfg: dict) -> None:
        mw.addonManager.writeConfig(ADDON_MODULE, cfg)

    def _restore_splitter_sizes(self) -> None:
        sizes = self._read_addon_cfg().get("ui", {}).get("main_splitter_sizes", [])
        if (
            isinstance(sizes, list)
            and len(sizes) == 2
            and all(isinstance(v, int) and v > 0 for v in sizes)
        ):
            sizes[0] = max(sizes[0], self.LEFT_PANEL_MIN_W)
            sizes[1] = max(sizes[1], self.PREVIEW_MIN_WIDTH)
            self.main_splitter.setSizes(sizes)

    def _save_splitter_sizes(self) -> None:
        if not hasattr(self, "main_splitter"):
            return
        cfg = self._read_addon_cfg()
        ui = cfg.get("ui", {})
        ui["main_splitter_sizes"] = self.main_splitter.sizes()
        cfg["ui"] = ui
        self._write_addon_cfg(cfg)

    def done(self, r: int) -> None:
        self._save_splitter_sizes()
        super().done(r)

    # ── Actions ────────────────────────────────────────────────────────────────

    def _do_backup(self):
        if not self._note_model or not self._card_tmpl:
            QMessageBox.warning(self, "Nothing to backup",
                                "Select a Note Type and Card Template first.")
            return
        create_backup(self._note_model, self._card_tmpl)
        QMessageBox.information(
            self, "Backup saved",
            f"Backed up: {self._note_model['name']} / {self._card_tmpl['name']}"
        )

    def _do_restore(self):
        backups = get_all_backups()
        if not backups:
            QMessageBox.information(self, "No backups", "No backups found.")
            return
        dlg = RestoreDialog(self, backups)
        if dlg.exec() != QDialog.DialogCode.Accepted or not dlg.selected_id:
            return
        ok, err = restore_backup(dlg.selected_id)
        if ok:
            QMessageBox.information(self, "Restored", "Template restored successfully.")
        else:
            QMessageBox.critical(self, "Restore failed", err or "Unknown error.")

    def _do_reset_to_defaults(self) -> None:
        if not self._note_model:
            return
        front_fields    = self.front_list.get_fields()
        back_fields     = self.back_list.get_fields()
        unmapped_fields = self.unmapped_list.get_fields()

        self.front_list.on_changed    = None
        self.back_list.on_changed     = None
        self.unmapped_list.on_changed = None
        self.front_list.clear()
        self.back_list.clear()
        self.unmapped_list.clear()

        for idx, f in enumerate(front_fields):
            if f.get("virtual"):
                self.front_list.add_field(f)
            else:
                self.front_list.add_field(self._make_field_dict(f["name"], is_front=True, index=idx))
        for idx, f in enumerate(back_fields, start=1):
            if f.get("virtual"):
                self.back_list.add_field(f)
            else:
                self.back_list.add_field(self._make_field_dict(f["name"], is_front=False, index=idx))
        for idx, f in enumerate(unmapped_fields):
            if f.get("virtual"):
                self.unmapped_list.add_field(f)
            else:
                self.unmapped_list.add_field(self._make_field_dict(f["name"], is_front=False, index=idx))

        self.front_list.on_changed    = self._on_fields_changed
        self.back_list.on_changed     = self._on_fields_changed
        self.unmapped_list.on_changed = self._on_fields_changed
        self._sync_fields_from_lists()
        self._save_note_state()
        self._refresh_preview()

    def _do_apply(self):
        if not self._note_model:
            QMessageBox.warning(self, "No Note Type", "Select a Note Type first.")
            return
        if not self._card_tmpl:
            QMessageBox.warning(self, "No Card Template", "Select a Card Template first.")
            return
        if not self._tmpl_cfg:
            QMessageBox.warning(self, "No Template", "Select a Prettify Template first.")
            return

        mn      = self._note_model["name"]
        tn      = self._card_tmpl["name"]
        cur_ord = self._card_tmpl["ord"]

        # Collect other card templates that have saved states → auto-apply in sync
        cfg_snap   = self._read_addon_cfg()
        note_draft = cfg_snap.get("note_states", {}).get(mn, {})
        if "prettify_template" in note_draft or "front_fields" in note_draft:
            note_draft = {}

        other_cards: list[tuple[dict, dict]] = []
        for tmpl in get_card_templates(self._note_model):
            if tmpl["ord"] == cur_ord:
                continue
            state = note_draft.get(tmpl.get("name", ""))
            if isinstance(state, dict) and "front_fields" in state:
                other_cards.append((tmpl, state))

        # Confirmation
        also_lines = "".join(
            f"\n  Also applying: {t['name']} (synced)" for t, _ in other_cards
        )
        reply = QMessageBox.question(
            self, "Apply Template",
            f"This will overwrite the template for:\n\n"
            f"  Note Type:     {mn}\n"
            f"  Card Template: {tn}{also_lines}\n\n"
            f"A backup will be created automatically.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        create_backup(self._note_model, self._card_tmpl)
        for other_tmpl, _ in other_cards:
            create_backup(self._note_model, other_tmpl)

        self._sync_fields_from_lists()
        self._save_note_state()
        lh = self._line_height_spin.value() if hasattr(self, "_line_height_spin") else 1.0
        fg = self._field_gap_spin.value() if hasattr(self, "_field_gap_spin") else -1

        # Build combined CSS: current card + unique fields from all other applied cards
        seen: set[str] = {
            f["name"] for f in self._front_fields + self._back_fields if f.get("name")
        }
        extra_fields: list[dict] = []

        for _, state in other_cards:
            for f in state.get("front_fields", []) + state.get("back_fields", []):
                if f.get("name") and not f.get("virtual") and f["name"] not in seen:
                    extra_fields.append(f)
                    seen.add(f["name"])

        # Also keep fields from previously applied cards that are NOT being re-applied
        prev_applied  = cfg_snap.get("applied_note_states", {}).get(mn, {})
        applied_keys  = {tn} | {t["name"] for t, _ in other_cards}
        for ak, astate in prev_applied.items():
            if ak == "_global" or ak in applied_keys or not isinstance(astate, dict):
                continue
            for f in astate.get("front_fields", []) + astate.get("back_fields", []):
                if f.get("name") and not f.get("virtual") and f["name"] not in seen:
                    extra_fields.append(f)
                    seen.add(f["name"])

        css = build_css(
            self._tmpl_cfg, self._front_fields, self._back_fields + extra_fields,
            line_height=lh,
            field_gap=fg if fg >= 0 else None,
            card_bg_light=self._card_bg_rgba(),
            card_bg_dark=self._card_bg_dark_rgba(),
            hr_style=self._hr_style,
            compare_field_dicts=self._compare_style_dicts(),
        )

        try:
            # Set current card's HTML
            front_html = build_front(self._front_fields, preview=False)
            back_html  = build_back(self._front_fields, self._back_fields, preview=False)
            for tmpl in self._note_model["tmpls"]:
                if tmpl["ord"] == cur_ord:
                    tmpl["qfmt"] = front_html
                    tmpl["afmt"] = back_html
                    break

            # Set other cards' HTML
            for other_tmpl, state in other_cards:
                of = state.get("front_fields", [])
                ob = state.get("back_fields", [])
                for tmpl in self._note_model["tmpls"]:
                    if tmpl["ord"] == other_tmpl["ord"]:
                        tmpl["qfmt"] = build_front(of, preview=False)
                        tmpl["afmt"] = build_back(of, ob, preview=False)
                        break

            # Set shared CSS and save model once
            self._note_model["css"] = css
            save_model(self._note_model)

            self._has_applied = True

            cfg = self._read_addon_cfg()
            applied         = cfg.get("applied_note_states", {})
            note_states_now = cfg.get("note_states", {}).get(mn, {})
            if "prettify_template" in note_states_now or "front_fields" in note_states_now:
                note_states_now = {}

            per_applied = applied.get(mn, {})
            if "prettify_template" in per_applied or "front_fields" in per_applied:
                per_applied = {}

            per_applied["_global"] = note_states_now.get("_global", {})
            per_applied[tn]        = note_states_now.get(tn, {})
            for other_tmpl, _ in other_cards:
                ok = other_tmpl.get("name", "")
                per_applied[ok] = note_states_now.get(ok, {})

            applied[mn] = per_applied
            cfg["applied_note_states"] = applied
            self._write_addon_cfg(cfg)

            if other_cards:
                other_names = ", ".join(f'"{t["name"]}"' for t, _ in other_cards)
                done_msg = (
                    f'Template applied to "{tn}" and {other_names} in "{mn}".\n\n'
                    f"Open the card browser to verify the result."
                )
            else:
                done_msg = (
                    f'Template applied to "{tn}" in "{mn}".\n\n'
                    f"Open the card browser to verify the result."
                )
            QMessageBox.information(self, "Done", done_msg)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply template:\n{e}")

    def closeEvent(self, event) -> None:
        for attr in ("preview_front", "preview_back"):
            w = getattr(self, attr, None)
            if w and hasattr(w, "cleanup"):
                try:
                    w.cleanup()
                except Exception:
                    pass
        cfg = self._read_addon_cfg()
        cfg.pop("note_states", None)
        self._write_addon_cfg(cfg)
        super().closeEvent(event)
