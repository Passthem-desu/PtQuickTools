import sys
from PySide6 import QtWidgets
from widgets.SearchWindow import SearchWindow
import putils.SettingsLoader as SettingsLoader
import putils.ThemeLoader as ThemeLoader


if __name__ == "__main__":
    SettingsLoader.loadSettings()
    ThemeLoader.prepareTheme(SettingsLoader.SettingsLoader.CURRENT_SETTINGS.theme)

    app = QtWidgets.QApplication()

    widget = SearchWindow(app)

    sys.exit(app.exec())
