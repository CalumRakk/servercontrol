

from labcontrol.config import Config as LabConfig
from labcontrol.parser import parse_lab_aws_details_content
from labcontrol.schema import AWSContent, AWSStatus
from labcontrol.utils import get_params_with_config
from labcontrol.vocareum_http import VocareumApi
from pyrogram import enums

from .utils import should_wait_get_params


def echo(client, message):
    message.reply(message.text)

def help(client, message):
    message.reply("Comandos disponibles: /status")

def get_aws_status(client, message, config: LabConfig):
    try:
        if should_wait_get_params(config):
            message.reply("Esperando a que se obtenga la información de Vocareum. Esto puede toma un tiempo.")

        params= get_params_with_config(config)
        vocareum_api = VocareumApi(params)

        result = vocareum_api.get_aws_status()
        if result.success is True:
            message.reply(result.status.value)
        else:
            message.reply("No se pudo obtener el estado de AWS. Intente de nuevo.")
            config.vocareum_cookies_path.unlink(missing_ok=True)
    except Exception as e:
        message.reply(str(e))

def get_aws(client, message, config: LabConfig):
    try:
        if should_wait_get_params(config):
            message.reply("Esperando a que se obtenga la información de Vocareum. Esto puede toma un tiempo.")

        params= get_params_with_config(config)
        vocareum_api = VocareumApi(params)

        result = vocareum_api.get_aws()
        if isinstance(result, AWSStatus):
            if result.success is True:
                msg= f"Parece que la maquina se esta encendiendo. Por favor, espera un momento. Lab status: {result.status.value}"
                message.reply(msg)
                return
        elif isinstance(result, AWSContent):
            if result.success is True:
                content_parsed= parse_lab_aws_details_content(result.content)
                message.reply(content_parsed.model_dump_json(indent=4), parse_mode=enums.ParseMode.MARKDOWN)
                return
            
        message.reply("No se pudo obtener el estado de AWS. Intente de nuevo.")
        config.vocareum_cookies_path.unlink(missing_ok=True)
    except Exception as e:
        message.reply(str(e))