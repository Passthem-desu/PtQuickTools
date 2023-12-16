import global_hotkeys
from putils.SettingsLoader import SettingsLoader
from PySide6 import QtCore
from typing import Any


class HotkeyEventEmitter(QtCore.QObject):
    callout = QtCore.Signal(name="calloutHotkey")


hotkeyEventEmitter = HotkeyEventEmitter()


def init():
    loadHotkeys()
    global_hotkeys.start_checking_hotkeys()

def loadHotkeys():
    global_hotkeys.clear_hotkeys()

    global_hotkeys.register_hotkey(SettingsLoader.CURRENT_SETTINGS.hotkeys.callout, lambda: hotkeyEventEmitter.callout.emit(), None)

def quit():
    global_hotkeys.stop_checking_hotkeys()