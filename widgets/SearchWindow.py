import logging
from PySide6 import QtWidgets, QtCore
from PySide6.QtGui import (
    QCloseEvent,
    QPaintEvent,
    QPainter,
    QBrush,
    QColor,
    QMouseEvent,
    QKeyEvent,
)
from putils.ThemeLoader import getSourceText, SourceName, ThemeLoader
import pyautogui

import putils.HotkeyManager as HotkeyManager
import putils.SettingsLoader as SettingsLoader


class SearchWindowInput(QtWidgets.QLineEdit):
    def __init__(self, parent: "SearchWindow"):
        super().__init__(parent=parent)
        self.__parent = parent

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if (
            event.key() == QtCore.Qt.Key.Key_Enter
            or event.key() == QtCore.Qt.Key.Key_Return
        ):
            self.__parent.runCommand()
        elif event.key() == QtCore.Qt.Key.Key_Escape:
            self.__parent.hideWindow()
        else:
            super().keyPressEvent(event)


class SearchWindow(QtWidgets.QWidget):
    def __init__(self, app: QtWidgets.QApplication):
        super().__init__()

        self.app = app

        self.setWindowFlag(
            QtCore.Qt.WindowType.FramelessWindowHint
            | QtCore.Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)

        self.__line_edit = SearchWindowInput(self)

        self.setTheme()

        HotkeyManager.init()
        HotkeyManager.hotkeyEventEmitter.callout.connect(self.callout)

        self.__check_focused_timer = QtCore.QTimer(self)
        self.__check_focused_timer.setInterval(100)
        self.__check_focused_timer.timeout.connect(self.checkFocusOut)
        self.__check_focused_timer.start()

        self._move_drag = False
        self._m_position = QtCore.QPoint(0, 0)

        self._dialog_running = False

    def text(self):
        return self.__line_edit.text()

    def runCommand(self):
        if self.text().replace(" ", "") == "":
            self.hideWindow()
            return
    
        command = self.text().strip()

        if command == "心水湛清":
            dialog = QtWidgets.QMessageBox(self)
            dialog.setWindowTitle("心水湛清")
            dialog.setText("是给")
            dialog.exec()
            return
        
        if SettingsLoader.SettingsLoader.CURRENT_SETTINGS.hideWindowIfError:
            logging.info("分析指令的时候出问题了，但是设置里面说遇到问题也不管，直接隐藏窗口了，所以就没有提示消息了。")
            
            self.hideWindow()
            return
            
        self._dialog_running = True
        dialog = QtWidgets.QMessageBox(self)
        dialog.setWindowTitle("错误")
        dialog.setText(f"未知的指令 {self.text()}。")
        dialog.exec()
        self._dialog_running = False

    def setTheme(self):
        self.__line_edit.setFixedSize(
            QtCore.QSize(
                ThemeLoader.CURRENT_THEME.inputAreaWidth,
                ThemeLoader.CURRENT_THEME.inputAreaHeight,
            )
        )

        self.__line_edit.move(
            ThemeLoader.CURRENT_THEME.inputMarginWidth,
            ThemeLoader.CURRENT_THEME.inputMarginWidth,
        )

        self.setStyleSheet(getSourceText(SourceName.SearchInputWindowStyleSheet))
        self.setFixedSize(
            QtCore.QSize(
                ThemeLoader.CURRENT_THEME.inputAreaWidth
                + ThemeLoader.CURRENT_THEME.inputMarginWidth * 2,
                ThemeLoader.CURRENT_THEME.inputAreaHeight
                + ThemeLoader.CURRENT_THEME.inputMarginWidth * 2,
            )
        )

        shadow = QtWidgets.QGraphicsDropShadowEffect(self)
        shadow.setOffset(
            ThemeLoader.CURRENT_THEME.shadowOffsetX,
            ThemeLoader.CURRENT_THEME.shadowOffsetY,
        )
        shadow.setColor(QColor(0, 0, 0, 45))
        shadow.setBlurRadius(ThemeLoader.CURRENT_THEME.shadowBlurRadius)
        self.setGraphicsEffect(shadow)

    def paintEvent(self, _: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setBrush(QBrush(ThemeLoader.CURRENT_THEME.backgroundColor))
        painter.setPen(QColor("#00000000"))
        painter.drawRoundedRect(
            ThemeLoader.CURRENT_THEME.inputMarginWidth
            - ThemeLoader.CURRENT_THEME.paintPaddingWidth,
            ThemeLoader.CURRENT_THEME.inputMarginWidth
            - ThemeLoader.CURRENT_THEME.paintPaddingHeight,
            ThemeLoader.CURRENT_THEME.paintPaddingWidth * 2
            + ThemeLoader.CURRENT_THEME.inputAreaWidth,
            ThemeLoader.CURRENT_THEME.paintPaddingHeight * 2
            + ThemeLoader.CURRENT_THEME.inputAreaHeight,
            ThemeLoader.CURRENT_THEME.borderRadius,
            ThemeLoader.CURRENT_THEME.borderRadius,
        )

    def isFocused(self):
        return self.__line_edit.hasFocus() or self._dialog_running

    def hideWindow(self):
        self.hide()
        self.__line_edit.setText("")

    def checkFocusOut(self):
        if not self.isFocused():
            self.hideWindow()

    def callout(self):
        self.__line_edit.setFocus(QtCore.Qt.FocusReason.PopupFocusReason)
        self.__line_edit.setText("")

        x, y = pyautogui.position()
        winx, winy = (
            x - ThemeLoader.CURRENT_THEME.inputAreaWidth // 2,
            y - ThemeLoader.CURRENT_THEME.inputAreaHeight,
        )
        winx, winy = (
            int(max(0, min(winx, pyautogui.size()[0])) / self.devicePixelRatio())
            - ThemeLoader.CURRENT_THEME.inputMarginWidth,
            int(max(0, min(winy, pyautogui.size()[1])) / self.devicePixelRatio())
            - ThemeLoader.CURRENT_THEME.inputMarginWidth,
        )

        self.move(winx, winy)

        self.show()

        pyautogui.leftClick()

    def closeEvent(self, event: QCloseEvent) -> None:
        HotkeyManager.quit()
        event.accept()

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._move_drag = True
            self._m_position = event.globalPos() - self.pos()
        event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._move_drag:
            self.move(event.globalPos() - self._m_position)
        event.accept()

    def mouseReleaseEvent(self, _: QMouseEvent) -> None:
        self._move_drag = False
