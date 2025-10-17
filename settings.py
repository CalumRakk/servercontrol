import os
import sys
from os import getenv
from pathlib import Path
from platform import system
from typing import List, Optional, Union, cast

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_user_config_dir(app_name: str) -> Path:
    if sys.platform.startswith("win"):
        # En Windows se usa APPDATA → Roaming
        path= Path(cast(str, getenv("APPDATA"))) / app_name
        path.mkdir(parents=True, exist_ok=True)
        return path
    elif sys.platform == "darwin":
        # En macOS
        path= Path.home() / "Library" / "Application Support" / app_name
        path.mkdir(parents=True, exist_ok=True)
        return path
    else:
        # En Linux / Unix
        path= Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config")) / app_name
        path.mkdir(parents=True, exist_ok=True)
        return path


class Settings(BaseSettings):
    bot_token: str

    # Opcionales
    api_hash: str = Field(
        description="Telegram API hash", default="d524b414d21f4d37f08684c1df41ac9c"
    )
    api_id: int = Field(description="Telegram API ID", default=611335)
    session_name: str = "me"
    app_name: str = "server_mc_9000"
    worktable: Path = Path(get_user_config_dir(app_name)).resolve()

def get_settings(env_path: Union[Path, str] = ".env") -> Settings:
    """
    Carga configuración desde un archivo .env

    La utilidad principal es ocultar el falso positivo de pylance al advertir que faltan argumentos que van a ser cargados desde el archivo .env
    Ver https://github.com/pydantic/pydantic/issues/3753
    """
    env_path = Path(env_path) if isinstance(env_path, str) else env_path
    try:
        if env_path.exists():
            settings = Settings(_env_file=env_path)  # type: ignore
            return settings
        raise FileNotFoundError(f"El archivo de configuración {env_path} no existe.")
    except ValidationError as e:
        print("❌ Error en configuración:", e)
        raise