import os
import sys
from os import getenv
from pathlib import Path
from typing import Union, cast

from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings


def get_user_config_dir(app_name: str) -> Path:
    if sys.platform.startswith("win"):
        # En Windows se usa APPDATA → Roaming
        path = Path(cast(str, getenv("APPDATA"))) / app_name
        path.mkdir(parents=True, exist_ok=True)
        return path
    elif sys.platform == "darwin":
        # En macOS
        path = Path.home() / "Library" / "Application Support" / app_name
        path.mkdir(parents=True, exist_ok=True)
        return path
    else:
        # En Linux / Unix
        path = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / app_name
        path.mkdir(parents=True, exist_ok=True)
        return path


class TelegramConfig(BaseSettings):
    bot_token: str
    api_hash: str = Field(description="Telegram API hash")
    api_id: int = Field(description="Telegram API ID")


    session_name: str = "me"
    app_name: str = "server_mc_9000"
    worktable: Path = Path(get_user_config_dir(app_name)).resolve()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


def load_config(env_path: Union[Path, str] = ".env") -> TelegramConfig:
    env_path = Path(env_path) if isinstance(env_path, str) else env_path
    try:
        if env_path.exists():
            settings = Config(_env_file=env_path)  # type: ignore
            return settings
        raise FileNotFoundError(f"El archivo de configuración {env_path} no existe.")
    except ValidationError as e:
        print("Error en configuración:", e)
        raise
