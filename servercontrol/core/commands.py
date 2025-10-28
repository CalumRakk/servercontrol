from pathlib import Path
from typing import cast

from labcontrol.config import Config as LabConfig
from labcontrol.parser import parse_lab_aws_details_content
from labcontrol.schema import AWSDetailsRunning, LabStatus
from labcontrol.utils import get_params_with_config
from labcontrol.vocareum_http import VocareumApi
from pyrogram import enums

from .utils import should_wait_get_params

ADMIN_IDS = [int(i) for i in Path("admin_ids.txt").read_text().splitlines()]


def echo(client, message):
    message.reply(message.text)


def help(client, message):
    message.reply(
        "Comandos disponibles:\n"
        " /pc_status - Obtiene el estado de la máquina.\n"
        " /pc_start - Enciende la máquina o reinicia el tiempo de apago.\n"
        " /pc_end - Apaga la máquina.\n"
        " /pc_details - Obtiene los detalles de la máquina.\n"
        " /pc_sso - Obtiene el enlace SSO de AWS.\n"
    )


# ============================================================
# Helpers
# ============================================================


def ensure_admin(message):
    """Verifica si el usuario tiene permisos de administrador."""
    if message.from_user.id not in ADMIN_IDS:
        message.reply("No tienes permiso para usar este comando.")
        return False
    return True


def prepare_vocareum_api(message, config: LabConfig) -> VocareumApi:
    """Inicializa VocareumApi, verificando esperas y errores comunes."""
    if should_wait_get_params(config):
        message.reply(
            "Obteniendo la session de Vocareum. Esto puede tardar hasta 1 minuto, por favor espere."
        )
    params = get_params_with_config(config)
    return VocareumApi(params)


def handle_api_error(
    message,
    config: LabConfig,
    msg="No se pudo obtener el estado de AWS. Intente de nuevo.",
):
    """Maneja errores comunes de Vocareum."""
    message.reply(msg)
    config.vocareum_cookies_path.unlink(missing_ok=True)


# ============================================================
# Comandos principales
# ============================================================


def get_aws_status(client, message, config: LabConfig):
    try:
        vocareum_api = prepare_vocareum_api(message, config)
        result = vocareum_api.get_aws_status()

        if result.success is True:
            message.reply(f"Estado de la Máquina: {result.status.value}")
        else:
            handle_api_error(message, config)
    except Exception as e:
        message.reply(str(e))


def start_aws(client, message, config: LabConfig):
    try:
        if not ensure_admin(message):
            return
        is_creation = False
        vocareum_api: VocareumApi = prepare_vocareum_api(message, config)
        status_result = vocareum_api.get_aws_status()
        if status_result.success is False:
            return handle_api_error(message, config)

        if status_result.status == LabStatus.in_creation:
            message.reply("La máquina ya se está encendiendo...")
            return
        elif status_result.status == LabStatus.ready:
            message.reply(
                "La Máquina está encendida, reiniciando el tiempo de apagado..."
            )
        elif status_result.status == LabStatus.stopped:
            message.reply("Por favor espera a que se encienda la Máquina...")
            is_creation = True
        else:
            message.reply("No se pudo obtener el estado de AWS. Intente de nuevo.")
            return

        result = vocareum_api.start_aws()
        if result.success is False:
            return handle_api_error(message, config)

        if is_creation:
            message.reply("Encendiendo la Máquina...")
            vocareum_api._wait_if_in_creation()
            message.reply("Máquina encendida con éxito.")
            message.reply(
                "La Máquina se apagará en 4 horas. Recuerda usar /pc_start para reiniciar el tiempo de apagado."
            )
        else:
            message.reply("Tiempo de apagado de Máquina restablecido.")

    except Exception as e:
        message.reply(str(e))


def end_aws(client, message, config: LabConfig):
    try:
        if not ensure_admin(message):
            return

        vocareum_api = prepare_vocareum_api(message, config)
        status_result = vocareum_api.get_aws_status()
        if status_result.success is False:
            return handle_api_error(message, config)

        if status_result.status == LabStatus.in_creation:
            message.reply(
                "La Máquina se está encendiendo. Por favor, espera un momento para apagarla."
            )
            vocareum_api._wait_if_in_creation()
        elif status_result.status == LabStatus.stopped:
            message.reply("La Máquina ya estaba apagada.")
            return

        message.reply("Apagando la Máquina...")
        result = vocareum_api.end_aws()
        if result.success is False:
            return handle_api_error(message, config)

        message.reply("Máquina apagada con exito.")
    except Exception as e:
        message.reply(str(e))


def get_aws_sso(client, message, config: LabConfig):
    try:
        if not ensure_admin(message):
            return

        vocareum_api = prepare_vocareum_api(message, config)
        result = vocareum_api.get_aws_status()
        if result.success is False:
            return handle_api_error(message, config)

        if result.status != LabStatus.ready:
            message.reply("La Máquina no está encendida. No se puede obtener SSO.")
            return

        message.reply("Obteniendo SSO de AWS...")
        content = vocareum_api.get_aws()
        if content.success is False:
            return handle_api_error(message, config)

        content_parsed = cast(
            AWSDetailsRunning, parse_lab_aws_details_content(content.content)
        )
        result = vocareum_api.get_aws_sso(content_parsed.aws_sso)
        message.reply(
            f"Enlace SSO de AWS: `{result}`", parse_mode=enums.ParseMode.MARKDOWN
        )
    except Exception as e:
        message.reply(str(e))


def get_aws(client, message, config: LabConfig):
    try:
        if not ensure_admin(message):
            return

        vocareum_api = prepare_vocareum_api(message, config)
        status_result = vocareum_api.get_aws_status()
        if status_result.success is False:
            return handle_api_error(message, config)

        message.reply("Obteniendo detalles de la Máquina...")
        result = vocareum_api.get_aws()
        if result.success is False:
            return handle_api_error(message, config)

        content_parsed = parse_lab_aws_details_content(result.content)
        text_message = f"""
**Detalles de la Máquina**
```json
{content_parsed.model_dump_json(indent=4)}
```
"""
        message.reply(
            text_message,
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    except Exception as e:
        message.reply(str(e))
