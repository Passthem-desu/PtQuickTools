from enum import Enum
import os


class QSSSources(Enum):
    SearchWindowStyle = "SearchWindow.qss"


def findFiles(*filePaths: str):
    for tryPath in filePaths:
        if os.path.exists(tryPath):
            return tryPath

    raise FileNotFoundError(
        "没有在下列文件列表中找到资源文件：\n  " + "\n  ".join(filePaths)
    )


def getThemedFileLink(fileName: str, theme: str):
    return findFiles(
        os.path.join(os.getcwd(), "sources", "themes", theme, fileName),
        os.path.join(os.getcwd(), "sources", "themes", "default", fileName),
    )


def loadQSS(location: QSSSources, theme: str = "defalut"):
    with open(getThemedFileLink(location.value, theme), "r", encoding="utf-8") as f:
        return f.read()
