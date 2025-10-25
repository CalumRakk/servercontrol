

from pathlib import Path

from labcontrol.config import Config as LabConfig
from labcontrol.schema import AWSStatus, LabStatus
from labcontrol.utils import get_params_with_config
from labcontrol.vocareum_http import VocareumApi
from pyrogram import enums

from .utils import should_wait_get_params

ADMIN_IDS=[int(i) for i in  Path("admin_ids.txt").read_text().splitlines()]

def echo(client, message):
    message.reply(message.text)

def help(client, message):
    message.reply("Comandos disponibles:\n /status - Obtiene el estado de la maquina.\n /start - Enciende la maquina.\n /end - Apaga la maquina.")

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

# def get_aws(client, message, config: LabConfig):
#     try:
#         if should_wait_get_params(config):
#             message.reply("Esperando a que se obtenga la información de Vocareum. Esto puede toma un tiempo.")

#         params= get_params_with_config(config)
#         vocareum_api = VocareumApi(params)

#         result = vocareum_api.get_aws()
#         if isinstance(result, AWSStatus):
#             if result.success is True:
#                 msg= f"Parece que la maquina se esta encendiendo. Por favor, espera un momento. Lab status: {result.status.value}"
#                 message.reply(msg)
#                 return
#         elif isinstance(result, AWSContent):
#             if result.success is True:
#                 content_parsed= parse_lab_aws_details_content(result.content)
#                 message.reply(content_parsed.model_dump_json(indent=4), parse_mode=enums.ParseMode.MARKDOWN)
#                 return
            
#         message.reply("No se pudo obtener el estado de AWS. Intente de nuevo.")
#         config.vocareum_cookies_path.unlink(missing_ok=True)
#     except Exception as e:
#         message.reply(str(e))


def start_aws(client, message, config: LabConfig):
    try:
        if not message.from_user.id in ADMIN_IDS:
            message.reply("No tienes permiso para usar este comando.")
            return

        if should_wait_get_params(config):
            message.reply("Esperando a que se obtenga la información de Vocareum. Esto puede toma un tiempo.")

        params= get_params_with_config(config)
        vocareum_api = VocareumApi(params)

        stus_result= vocareum_api.get_aws_status()
        if stus_result.success is True:
            if stus_result.status == LabStatus.in_creation:
                message.reply("Encendiendo una maquina que se esta encendiendo...")
                return
            elif stus_result.status == LabStatus.ready:  
                message.reply("Encendiendo una maquina encendida...")         

        result = vocareum_api.start_aws()
        if isinstance(result, AWSStatus):
            if result.success is True:
                msg= f"Parece que la maquina se esta encendiendo. Por favor, espera un momento. Lab status: {result.status.value}"
                message.reply(msg)
                return
  
        if result.success is True:            
            message.reply("Maquina en creación.", parse_mode=enums.ParseMode.MARKDOWN)
            return
            
        message.reply("No se pudo obtener el estado de AWS. Intente de nuevo.")
        config.vocareum_cookies_path.unlink(missing_ok=True)
    except Exception as e:
        message.reply(str(e))

def end_aws(client, message, config: LabConfig):
    try:
        if not message.from_user.id in ADMIN_IDS:
            message.reply("No tienes permiso para usar este comando.")
            return

        if should_wait_get_params(config):
            message.reply("Esperando a que se obtenga la información de Vocareum. Esto puede toma un tiempo.")

        params= get_params_with_config(config)
        vocareum_api = VocareumApi(params)

        stus_result= vocareum_api.get_aws_status()
        if stus_result.success is True:
            if stus_result.status == LabStatus.in_creation:
                message.reply("Apagando una maquina que se está encendiendo...")    
            elif stus_result.status == LabStatus.ready:  
                message.reply("Apagando una maquina encendida...")         

        result = vocareum_api.end_aws()
        if isinstance(result, AWSStatus):
            if result.success is True:
                msg= f"Parece que la maquina se esta encendiendo o apagando.. Por favor, espera un momento. Lab status: {result.status.value}"
                message.reply(msg)
                return
   
        if result.success is True:
            message.reply("Maquina detenida.", parse_mode=enums.ParseMode.MARKDOWN)
            return
        
        message.reply("No se pudo obtener el estado de AWS. Intente de nuevo.")
        config.vocareum_cookies_path.unlink(missing_ok=True)
    except Exception as e:
        message.reply(str(e))