import sys
from PySide6 import QtWidgets
from widgets.SearchWindow import SearchWindow
import putils.LoadSettings as LoadSettings


if __name__ == "__main__":
    LoadSettings.loadSettings()

    app = QtWidgets.QApplication([])

    widget = SearchWindow(app)

    sys.exit(app.exec())
