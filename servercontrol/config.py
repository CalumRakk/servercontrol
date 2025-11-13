from pathlib import Path
from typing import Literal, Union

from discord import Optional
from labcontrol.config import Config as LabConfig
from pydantic import Field, ValidationError
from pydantic_settings import BaseSettings

from .core.settings import TelegramConfig


class AWSConfig(BaseSettings):
    """Configuración específica para la interacción directa con AWS via boto3."""

    aws_instance_id: str = Field(..., description="ID de la instancia EC2 de AWS")
    aws_region: str = Field("us-east-1", description="Región de AWS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class DuckDNSConfig(BaseSettings):
    """Configuración específica para DuckDNS."""

    duckdns_domain: str = Field(..., description="Dominio de DuckDNS")
    duckdns_token: str = Field(..., description="Token de DuckDNS")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


class LabControlEnvVars(BaseSettings):
    """Clase temporal solo para leer las variables de labcontrol desde el .env"""

    unique_id: str
    password: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
class DiscordConfig(BaseSettings):
    """Configuración específica para Discord."""

    bot_token: str = Field(..., description="Token del bot de Discord")
    guild_id: Optional[int] = Field(None, description="ID del servidor de Discord para pruebas (opcional)")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"
        env_prefix = "DISCORD_"
class OrchestratorConfig(BaseSettings):
    """Configuración global para el script orquestador."""

    bot_platform: Literal["discord", "telegram", "both"] = "both"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

class ManagerConfig:
    def __init__(
        self,
        tg_config: TelegramConfig,
        lab_config: LabConfig,
        aws_config: AWSConfig,
        duckdns_config: DuckDNSConfig,        
        discord_config: DiscordConfig,
        orchestrator_config: OrchestratorConfig
    ) -> None:
        self.orchestrator_config = orchestrator_config 
        self.tg_config = tg_config
        self.lab_config = lab_config
        self.aws_config = aws_config
        self.duckdns_config = duckdns_config
        self.discord_config = discord_config
        


def load_config_orchestator(env_path: Union[Path, str] = ".env") -> ManagerConfig:
    """Carga la configuración combinada para el orquestador desde un archivo .env."""
    env_file = Path(env_path) if isinstance(env_path, str) else env_path
    if not env_file.exists():
        raise FileNotFoundError(f"El archivo de configuración {env_file} no existe.")

    try:
        tg_config = TelegramConfig(_env_file=env_file)  # type: ignore
        aws_config = AWSConfig(_env_file=env_file)  # type: ignore
        duckdns_config = DuckDNSConfig(_env_file=env_file)  # type: ignore

        lab_env_vars = LabControlEnvVars(_env_file=env_file)  # type: ignore
        lab_config = LabConfig(
            unique_id=lab_env_vars.unique_id, password=lab_env_vars.password
        ) # type: ignore
        discord_config=DiscordConfig(_env_file=env_file) # type: ignore
        orchestrator_config = OrchestratorConfig(_env_file=env_file) # type: ignore
        return ManagerConfig(
            tg_config=tg_config,
            lab_config=lab_config,
            aws_config=aws_config,
            duckdns_config=duckdns_config,
            discord_config=discord_config,
            orchestrator_config=orchestrator_config
        )
    except ValidationError as e:
        print(f"Error en la configuración del archivo {env_file}:\n{e}")
        raise
