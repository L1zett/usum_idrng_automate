import json
import os


class SettingKeys:
    TOKEN = "Token"
    THEME = "Theme"
    CONTROL_METHOD = "Control Methods"
    INACTIVE = "inactive"
    SCREENSHOT_PATH = "Screenshot Path"


class SettingsManager:
    def __init__(self, filepath=os.path.join(os.path.dirname(__file__), "settings.json")):
        self._filepath = filepath
        self._settings = {}

    def load_settings(self):
        try:
            with open(self._filepath, "r") as file:
                self._settings = json.load(file)
        except FileNotFoundError:
            self._settings = {}
        except json.JSONDecodeError:
            self._settings = {}

    def save_settings(self):
        with open(self._filepath, "w") as file:
            json.dump(self._settings, file, indent=4)

    def get(self, key, default=None):
        return self._settings.get(key, default)

    def set(self, key, value):
        self._settings[key] = value
