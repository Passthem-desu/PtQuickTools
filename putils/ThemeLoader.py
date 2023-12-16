from enum import Enum
from typing import List, Dict

import os
import pydantic
import base64
import logging
import json


class SourceType(Enum):
    RawSourceData = 0
    ReadFromFile = 1
    Base64 = 2
    FallbackToDefault = -1


class SourceName(Enum):
    SearchInputWindowStyleSheet = "searchInputWindowStyleSheet"


class SourceData(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    sourceType: SourceType
    sourceValue: str
    encoding: str = "utf-8"  # 只有读取比特流时，这个选项有用

    def getText(self, base=os.getcwd()) -> str:
        if self.sourceType == SourceType.FallbackToDefault:
            raise FileNotFoundError()
        if self.sourceType == SourceType.RawSourceData:
            return self.sourceValue
        if self.sourceType == SourceType.ReadFromFile:
            fp = os.path.join(base, self.sourceValue)
            if not os.path.exists(fp):
                raise FileNotFoundError(fp)
            with open(fp, "r", encoding=self.encoding) as f:
                return f.read()
        if self.sourceType == SourceType.Base64:
            return base64.b64decode(self.sourceValue).decode(self.encoding)
        raise ValueError()

    def getBytes(self, base=os.getcwd()) -> bytes:
        if self.sourceType == SourceType.FallbackToDefault:
            raise FileNotFoundError()
        if self.sourceType == SourceType.RawSourceData:
            return self.sourceValue.encode(self.encoding)
        if self.sourceType == SourceType.ReadFromFile:
            fp = os.path.join(base, self.sourceValue)
            if not os.path.exists(fp):
                raise FileNotFoundError(fp)
            with open(fp, "rb") as f:
                return f.read()
        if self.sourceType == SourceType.Base64:
            return base64.b64decode(self.sourceValue)
        raise ValueError()


class Attribute(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    attributeName: str
    attributeValue: str


class SourceDetailSettings(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    paintPaddingWidth: int = 20
    paintPaddingHeight: int = 5
    inputAreaWidth: int = 500
    inputAreaHeight: int = 40
    inputMarginWidth: int = 100
    shadowOffsetX: float = 0
    shadowOffsetY: float = 5
    shadowBlurRadius: float = 30
    borderRadius: float = 20
    backgroundColor: str = "#ffffff"


class ThemeSettings(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    detailedSettings: SourceDetailSettings = SourceDetailSettings()
    extraAttributes: List[Attribute] = []
    sources: Dict[SourceName, SourceData] = {}


class ThemeLoader:
    DEFAULT_THEME = ThemeSettings(
        sources={
            SourceName.SearchInputWindowStyleSheet: SourceData(
                sourceType=SourceType.ReadFromFile, sourceValue="SearchWindow.qss"
            )
        }
    )

    CURRENT_THEME: ThemeSettings = DEFAULT_THEME
    CURRENT_THEME_NAME: str = "default"

    SOURCE_TEXTS_CACHE: Dict[SourceName, str] = {}
    SOURCE_BYTES_CACHE: Dict[SourceName, bytes] = {}


def _getSourceText(name: SourceName) -> str:
    if name in ThemeLoader.CURRENT_THEME.sources.keys():
        try:
            return ThemeLoader.CURRENT_THEME.sources[name].getText(
                os.path.join(
                    os.getcwd(), "sources", "themes", ThemeLoader.CURRENT_THEME_NAME
                )
            )
        except:
            pass

    return ThemeLoader.DEFAULT_THEME.sources[name].getText(
        os.path.join(os.getcwd(), "sources", "themes", "default")
    )


def getSourceText(name: SourceName) -> str:
    if name in ThemeLoader.SOURCE_TEXTS_CACHE.keys():
        return ThemeLoader.SOURCE_TEXTS_CACHE[name]

    value = _getSourceText(name)
    ThemeLoader.SOURCE_TEXTS_CACHE[name] = value
    return value


def _getSourceBytes(name: SourceName) -> bytes:
    if name in ThemeLoader.CURRENT_THEME.sources.keys():
        try:
            return ThemeLoader.CURRENT_THEME.sources[name].getBytes(
                os.path.join(
                    os.getcwd(), "sources", "themes", ThemeLoader.CURRENT_THEME_NAME
                )
            )
        except:
            pass

    return ThemeLoader.DEFAULT_THEME.sources[name].getBytes(
        os.path.join(os.getcwd(), "sources", "themes", "default")
    )


def getSourceBytes(name: SourceName) -> bytes:
    if name in ThemeLoader.SOURCE_BYTES_CACHE.keys():
        return ThemeLoader.SOURCE_BYTES_CACHE[name]

    value = _getSourceBytes(name)
    ThemeLoader.SOURCE_BYTES_CACHE[name] = value
    return value


def clearValueCaches():
    ThemeLoader.SOURCE_TEXTS_CACHE = {}
    ThemeLoader.SOURCE_BYTES_CACHE = {}


def loadDefaultTheme():
    ThemeLoader.CURRENT_THEME = ThemeLoader.DEFAULT_THEME
    ThemeLoader.CURRENT_THEME_NAME = "default"

    clearValueCaches()


def prepareTheme(themeName: str):
    if themeName == "default":
        logging.info("加载默认主题")
        loadDefaultTheme()
        return
    
    fp = os.path.join(os.getcwd(), "sources", "themes", themeName, "theme")
    if not os.path.exists(fp):
        logging.warning(f"指定的主题 {themeName} 的文件不存在，将会加载默认主题")
        loadDefaultTheme()
        return

    try:
        ThemeLoader.CURRENT_THEME = ThemeSettings.parse_file(fp)
        ThemeLoader.CURRENT_THEME_NAME = themeName

        clearValueCaches()
    except json.JSONDecodeError as e:
        logging.warning(f"在读取主题设定的时候，JSON 解析出现了问题。将会加载默认主题。{e.msg}")
    except pydantic.ValidationError as e:
        logging.warning(f"在读取设置的时候，Pydantic 解析出现了问题。将会加载默认主题。")

        for error in e.errors():
            logging.warning(f"捕获到的错误：{error['type']}：{error['msg']}")
