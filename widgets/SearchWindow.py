from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import QCloseEvent, QPaintEvent, QPainter, QBrush
from putils.ThemeLoader import getSourceText, SourceName, ThemeLoader
import pyautogui

import putils.HotkeyManager as HotkeyManager
import putils.SettingsLoader as LoadSettings


class SearchWindow(QtWidgets.QWidget):
    def __init__(self, app: QtWidgets.QApplication):
        super().__init__()

        self.app = app

        self.setWindowFlag(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__line_edit = QtWidgets.QLineEdit(parent=self)

        self.setTheme()

        HotkeyManager.init()
        HotkeyManager.hotkeyEventEmitter.callout.connect(self.callout)

        self.__check_focused_timer = QtCore.QTimer(self)
        self.__check_focused_timer.setInterval(100)
        self.__check_focused_timer.timeout.connect(self.checkFocusOut)
        self.__check_focused_timer.start()

    def setTheme(self):
        self.__line_edit.setFixedSize(
            QtCore.QSize(
                ThemeLoader.CURRENT_THEME.detailedSettings.inputAreaWidth,
                ThemeLoader.CURRENT_THEME.detailedSettings.inputAreaHeight,
            )
        )

        self.__line_edit.move(
            ThemeLoader.CURRENT_THEME.detailedSettings.inputMarginWidth,
            ThemeLoader.CURRENT_THEME.detailedSettings.inputMarginWidth,
        )

        self.setStyleSheet(getSourceText(SourceName.SearchInputWindowStyleSheet))
        self.setFixedSize(
            QtCore.QSize(
                ThemeLoader.CURRENT_THEME.detailedSettings.inputAreaWidth
                + ThemeLoader.CURRENT_THEME.detailedSettings.inputMarginWidth * 2,
                ThemeLoader.CURRENT_THEME.detailedSettings.inputAreaHeight
                + ThemeLoader.CURRENT_THEME.detailedSettings.inputMarginWidth * 2,
            )
        )

    def paintEvent(self, _: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.fillRect(
            ThemeLoader.CURRENT_THEME.detailedSettings.inputMarginWidth
            - ThemeLoader.CURRENT_THEME.detailedSettings.paintPaddingWidth,
            ThemeLoader.CURRENT_THEME.detailedSettings.inputMarginWidth
            - ThemeLoader.CURRENT_THEME.detailedSettings.paintPaddingHeight,
            ThemeLoader.CURRENT_THEME.detailedSettings.paintPaddingWidth * 2
            + ThemeLoader.CURRENT_THEME.detailedSettings.inputAreaWidth,
            ThemeLoader.CURRENT_THEME.detailedSettings.paintPaddingHeight * 2
            + ThemeLoader.CURRENT_THEME.detailedSettings.inputAreaHeight,
            QBrush("#ffffff"),
        )

    def isFocused(self):
        return self.__line_edit.hasFocus()

    def checkFocusOut(self):
        if not self.isFocused():
            self.hide()

    def callout(self):
        self.__line_edit.setFocus(QtCore.Qt.FocusReason.PopupFocusReason)
        self.__line_edit.setText("")

        x, y = pyautogui.position()
        winx, winy = (
            x - ThemeLoader.CURRENT_THEME.detailedSettings.inputAreaWidth // 2,
            y - ThemeLoader.CURRENT_THEME.detailedSettings.inputAreaHeight,
        )
        winx, winy = (
            int(max(0, min(winx, pyautogui.size()[0])) / self.devicePixelRatio())
            - ThemeLoader.CURRENT_THEME.detailedSettings.inputMarginWidth,
            int(max(0, min(winy, pyautogui.size()[1])) / self.devicePixelRatio())
            - ThemeLoader.CURRENT_THEME.detailedSettings.inputMarginWidth,
        )

        self.move(winx, winy)

        self.show()

        pyautogui.leftClick()

    def closeEvent(self, event: QCloseEvent) -> None:
        HotkeyManager.quit()
        event.accept()
