from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QCloseEvent, QFocusEvent, QScreen
from putils.LoadSources import loadQSS, QSSSources
from typing import Any
import pyautogui

import putils.HotkeyManager as HotkeyManager
import putils.LoadSettings as LoadSettings


class SearchWindow(QtWidgets.QWidget):
    def __init__(self, app: QtWidgets.QApplication, theme: str = "default"):
        super().__init__()

        self.app = app

        self.setWindowFlag(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.__line_edit = QtWidgets.QLineEdit(parent=self)
        self.__line_edit.setFixedSize(
            QtCore.QSize(
                LoadSettings.CURRENT_SETTINGS.width,
                LoadSettings.CURRENT_SETTINGS.height,
            )
        )

        self.setStyleSheet(loadQSS(QSSSources.SearchWindowStyle, theme))
        self.setFixedSize(
            QtCore.QSize(
                LoadSettings.CURRENT_SETTINGS.width,
                LoadSettings.CURRENT_SETTINGS.height,
            )
        )

        HotkeyManager.init()
        HotkeyManager.hotkeyEventEmitter.callout.connect(self.callout)

        self.__check_focused_timer = QtCore.QTimer(self)
        self.__check_focused_timer.setInterval(100)
        self.__check_focused_timer.timeout.connect(self.checkFocusOut)
        self.__check_focused_timer.start()

    def isFocused(self):
        # return self.hasFocus() or self.__line_edit.hasFocus()

        return self.__line_edit.hasFocus()

    def checkFocusOut(self):
        if not self.isFocused():
            self.hide()

    def callout(self):
        self.__line_edit.setFocus(QtCore.Qt.FocusReason.PopupFocusReason)
        self.__line_edit.setText("")

        x, y = pyautogui.position()
        winx, winy = (
            x - LoadSettings.CURRENT_SETTINGS.width // 2,
            y - LoadSettings.CURRENT_SETTINGS.height,
        )
        winx, winy = int(
            max(0, min(winx, pyautogui.size()[0])) / self.devicePixelRatio()
        ), int(max(0, min(winy, pyautogui.size()[1])) / self.devicePixelRatio())

        self.move(winx, winy)

        self.show()

        pyautogui.leftClick()

    def closeEvent(self, event: QCloseEvent) -> None:
        HotkeyManager.quit()
        event.accept()
