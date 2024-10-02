from .singleton import SingletonMeta
import configparser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILEPATH = BASE_DIR / "config.ini"


class ManagerConfig(metaclass=SingletonMeta):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(CONFIG_FILEPATH)
        self.config = config

    def __getitem__(self, key):
        return self.config[key]

    def save(self):
        with open(CONFIG_FILEPATH, "w") as configfile:
            self.config.write(configfile)

    def get_credentials(self) -> tuple[str, str]:
        return self["account"]["username"], self["account"]["password"]
