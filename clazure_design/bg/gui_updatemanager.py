import os

from aqt.qt import QDialog, Qt
from aqt import mw
from aqt.utils import getFile, openFolder
from anki.utils import pointVersion

try:
    from .settings_dialog_qt6 import Ui_Dialog
except Exception:
    from .settings_dialog import Ui_Dialog

from .config import getUserOption, writeConfig, addon_path, getDefaultConfig

conf = getUserOption()

imgfolder = os.path.join(addon_path, "user_files")
RE_BG_IMG_EXT = "*.gif *.png *.apng *.jpg *.jpeg *.svg *.ico *.bmp"


class SettingsDialog(QDialog):
    timer = None

    def __init__(self, parent):
        QDialog.__init__(self, mw, Qt.WindowType.Window)
        mw.setupDialogGC(self)
        self.mw = mw
        self.parent = parent
        self.setupDialog()
        self.loadConfigData()
        self.setupConnections()
        self.exec()

    def reject(self):
        self.accept()
        self.close()

    def accept(self):
        QDialog.accept(self)
        self.close()

    def setupDialog(self):
        self.form = Ui_Dialog()
        self.form.setupUi(self)

    def setupConnections(self):
        f = self.form

        f.OkButton.clicked.connect(self.accept)
        f.RestoreButton.clicked.connect(self.resetConfig)
        f.pushButton_videoTutorial.setEnabled(False)

        f.pushButton_imageFolder.clicked.connect(lambda: openFolder(imgfolder))

        controller = {
            f.toolButton_background: (f.lineEdit_background,),
        }
        for btn, args in controller.items():
            btn.clicked.connect(lambda a="a", args=args: self._getFile(a, *args))

        controller = {
            f.checkBox_reviewer: ("Reviewer image",),
            f.checkBox_toolbar: ("Toolbar image",),
            f.checkBox_topbottom: ("Toolbar top/bottom",),
        }
        for cb, args in controller.items():
            cb.stateChanged.connect(lambda cb=cb, args=args: self._updateCheckbox(cb, *args))

        controller = {
            f.comboBox_attachment: ("background-attachment",),
            f.comboBox_position: ("background-position",),
            f.comboBox_size: ("background-size",),
        }
        for cb, args in controller.items():
            t = cb.currentText()
            cb.currentTextChanged.connect(lambda t=t, args=args: self._updateComboBox(t, *args))

        controller = {
            f.Slider_main: ("background opacity main",),
            f.Slider_review: ("background opacity review",),
        }
        for slider, args in controller.items():
            s = slider.value()
            slider.valueChanged.connect(lambda s=s, args=args: self._updateSliderLabel(s, *args))

        f.scaleBox.valueChanged.connect(self._updateSpinBox)

        a = f.lineEdit_background
        a.textChanged.connect(lambda t=a.text(): self._updateLineEdit(t, "Image name for background"))

    def loadConfigData(self):
        f = self.form

        c = conf["Reviewer image"]
        if f.checkBox_reviewer.isChecked() != c:
            f.checkBox_reviewer.click()

        c = conf["Toolbar image"]
        if f.checkBox_toolbar.isChecked() != c:
            f.checkBox_toolbar.click()

        c = conf["Toolbar top/bottom"]
        if f.checkBox_topbottom.isChecked() != c:
            f.checkBox_topbottom.click()

        f.comboBox_attachment.setCurrentText(conf["background-attachment"])
        f.comboBox_position.setCurrentText(conf["background-position"])
        f.comboBox_size.setCurrentText(conf["background-size"])

        f.Slider_main.setValue(int(float(conf["background opacity main"]) * 100))
        f.Slider_review.setValue(int(float(conf["background opacity review"]) * 100))

        f.scaleBox.setValue(float(conf["background scale"]))
        f.lineEdit_background.setText(conf["Image name for background"])

    def _getFile(self, pad, lineEditor, ext=RE_BG_IMG_EXT):
        def setWallpaper(path):
            f = path.split("user_files/background/")[-1]
            lineEditor.setText(f)

        getFile(
            mw,
            "Wallpaper",
            cb=setWallpaper,
            filter=ext,
            dir=f"{addon_path}/user_files/background",
        )

    def _updateCheckbox(self, cb, key):
        n = -1 if cb == 2 else 1
        v = True if n == -1 else False
        conf[key] = v
        writeConfig(conf)
        self._refresh()

    def _updateComboBox(self, text, key):
        conf[key] = text
        writeConfig(conf)
        self._refresh()

    def _updateSliderLabel(self, val, key):
        conf[key] = str(round(val / 100, 2))
        writeConfig(conf)
        self._refresh()

    def _updateSpinBox(self):
        f = self.form
        n = round(f.scaleBox.value(), 2)
        conf["background scale"] = str(n)
        writeConfig(conf)
        self._refresh()

    def _updateLineEdit(self, text, key):
        conf[key] = text
        writeConfig(conf)
        self._refresh()

    def resetConfig(self):
        global conf
        conf = getDefaultConfig()
        writeConfig(conf)
        self._refresh()
        self.close()
        SettingsDialogExecute()

    def _refresh(self, ms=100):
        if self.timer:
            self.timer.stop()

        if pointVersion() < 27:
            self.timer = mw.progress.timer(ms, lambda: mw.reset(True), False)
        elif pointVersion() < 45:
            self.timer = mw.progress.timer(ms, self._resetMainWindow, False)
        else:
            self.timer = mw.progress.timer(ms, lambda: mw.moveToState("deckBrowser"), False)

    def _resetMainWindow(self):
        mw.reset(True)
        mw.toolbar.draw()


def SettingsDialogExecute():
    SettingsDialog(mw)
