from pathlib import Path
from typing import Union

from labcontrol.config import Config as LabConfig
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings

from .core.settings import TelegramConfig


class GeneralConfig(BaseSettings):
    # Telegram
    bot_token: str
    api_hash: str = Field(description="Telegram API hash")
    api_id: int = Field(description="Telegram API ID")
    
    # Academy AWS
    unique_id: str
    password: str

class ManagerConfig():
    def __init__(self, tg_config: TelegramConfig, lab_config: LabConfig) -> None:
        self.tg_config= tg_config
        self.lab_config= lab_config
    

def load_config_orchestator(env_path: Union[Path, str] = ".env") -> ManagerConfig:
    """
    Carga el archivo de configuración de orchestra.

    Args:
        env_path (Union[Path, str], optional): El path al archivo de configuración. Por defecto es ".env". 
                                             Si es una ruta, se usa como string. 
        Debe ser un nombre de archivo que contenga las siguientes configuraciones:

            - BotToken
            - ApiId
            - ApiHash

    Returns:
        ManagerConfig: Objeto con las configuraciones específicas para Telegram y Lab.

    Raises:
        FileNotFoundError: Si el archivo de configuración no existe.
        ValidationError: Si hay errores en la configuración del archivo de configuración.
    """
    env_path = Path(env_path) if isinstance(env_path, str) else env_path
    try:
        if env_path.exists():                 
            client_client= GeneralConfig(_env_file=env_path)  # type: ignore
            
            tg_config= TelegramConfig(
                bot_token=client_client.bot_token, 
                api_id=client_client.api_id, api_hash=client_client.api_hash
            )
            lab_config= LabConfig(
                unique_id=client_client.unique_id, 
                password=client_client.password
            )
            return ManagerConfig(tg_config, lab_config)    
        

        raise FileNotFoundError(f"El archivo de configuración {env_path} no existe.")
    except ValidationError as e:
        print("❌ Error en configuración:", e)
        raise