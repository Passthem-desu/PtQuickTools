import pydantic
import os
import json
import logging
from global_hotkeys.keycodes import vk_key_names


class HotkeySettings(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    callout: str = "control + tab"

    @pydantic.validator("callout")
    def hotkeyValidating(cls, v: str):
        for key in v.split("+"):
            if key.replace(" ", "") not in vk_key_names.keys():
                raise ValueError("所给出的按键 " + key.replace(" ", "") + " 不在允许的按键列表中")
        return v


class Settings(pydantic.BaseModel, extra=pydantic.Extra.ignore):
    theme: str = "default"
    hotkeys: HotkeySettings = HotkeySettings()
    width: int = 500
    height: int = 50
    hideWindowIfError: bool = True


class SettingsLoader:
    CURRENT_SETTINGS = Settings()


def saveSettings(filePath: str = "settings.json"):
    _json = SettingsLoader.CURRENT_SETTINGS.json(exclude=set("model_config"))

    with open(os.path.join(os.getcwd(), filePath), "w", encoding="utf-8") as f:
        f.write(_json)


def loadSettings(filePath: str = "settings.json") -> Settings:
    fp = os.path.join(os.getcwd(), filePath)
    if os.path.exists(fp):
        with open(fp, "r", encoding="utf-8") as f:
            try:
                SettingsLoader.CURRENT_SETTINGS = Settings.parse_obj(json.load(f))
                saveSettings()
                return SettingsLoader.CURRENT_SETTINGS
            except json.JSONDecodeError as e:
                logging.warning(f"在读取设置的时候，JSON 解析出现了问题。于是只能初始化整个设置了：{e.msg}")
            except pydantic.ValidationError as e:
                logging.warning(f"在读取设置的时候，Pydantic 解析出现了问题。于是只能初始化整个设置了……")

                for error in e.errors():
                    logging.warning(f"捕获到的错误：{error['type']}：{error['msg']}")

    else:
        logging.info("没有找到文件哦……")
    
    SettingsLoader.CURRENT_SETTINGS = Settings()
    saveSettings()
    return SettingsLoader.CURRENT_SETTINGS
