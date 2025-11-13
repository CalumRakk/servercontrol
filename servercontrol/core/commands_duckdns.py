import time
from pathlib import Path
from typing import cast

import boto3
import requests
from labcontrol.schema import LabStatus

from servercontrol.config import ManagerConfig

from .commands_academy import (
    AWSDetailsRunning,
    ensure_admin,
    handle_api_error,
    parse_lab_aws_details_content,
    prepare_vocareum_api,
)

CHECK_INTERVAL = 7  # segundos entre verificaciones
MAX_WAIT = 120  # tiempo máximo de espera (segundos)


def wait_for_instance_ip(message, instance_id: str, region: str) -> str | None:
    """Espera hasta que la instancia EC2 tenga IP pública y esté 'running'."""
    ec2 = boto3.client("ec2", region_name=region)
    message.reply(f"Esperando a que la instancia {instance_id} esté lista...")

    start_time = time.time()
    while time.time() - start_time < MAX_WAIT:
        try:
            response = ec2.describe_instances(InstanceIds=[instance_id])
            instance = response["Reservations"][0]["Instances"][0]
            state = instance["State"]["Name"]
            ip = instance.get("PublicIpAddress")

            # message.reply(f"Estado: {state} | IP: {ip or 'Aún no asignada'}")

            if state == "running" and ip:
                return ip

            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            message.reply(f"Error al consultar la instancia: {e}")
            time.sleep(CHECK_INTERVAL)

    message.reply("Tiempo máximo de espera alcanzado. No se obtuvo IP pública.")
    return None


def update_duckdns(message, domain: str, token: str, ip: str | None) -> bool:
    """Actualiza la IP en DuckDNS."""
    params = {"domains": domain, "token": token, "ip": ip or "", "verbose": "true"}
    try:
        r = requests.get("https://www.duckdns.org/update", params=params)
        message.reply("Respuesta de DuckDNS:", r.text.strip())
        return "OK" in r.text
    except Exception as e:
        message.reply(f"Error actualizando DuckDNS: {e}")
        return False


def write_aws_credentials(message, credentials_text: str):
    """Escribe las credenciales de AWS en el archivo por defecto, compatible con Linux y Windows."""
    home_dir = Path.home()  # Detecta automáticamente /home/usuario o C:\Users\usuario
    aws_dir = home_dir / ".aws"
    credentials_file = aws_dir / "credentials"

    aws_dir.mkdir(parents=True, exist_ok=True)
    try:
        credentials_file.write_text(credentials_text.strip() + "\n", encoding="utf-8")
        message.reply(f"Credenciales de AWS escritas en {credentials_file}")
    except Exception as e:
        message.reply(f"Error al escribir credenciales de AWS: {e}")


# ============================================================
# Comandos principales
# ============================================================


def update_ip(client, message, config: ManagerConfig):
    try:
        if not ensure_admin(message):
            return

        vocareum_api = prepare_vocareum_api(message, config.lab_config)
        result = vocareum_api.get_aws_status()
        if result.success is False:
            return handle_api_error(message, config.lab_config)

        if result.status != LabStatus.ready:
            message.reply("La Máquina no está encendida. No se puede actualizar IP.")
            return

        message.reply("Obteniendo detalles de la Máquina...")
        result = vocareum_api.get_aws()
        if result.success is False:
            return handle_api_error(message, config.lab_config)

        content_parsed = cast(
            AWSDetailsRunning, parse_lab_aws_details_content(result.content)
        )
        write_aws_credentials(message, content_parsed.copy_and_paste_credentials)

        ip = wait_for_instance_ip(
            message, config.client.aws_instance_id, config.client.aws_region
        )
        if ip is None:
            message.reply("No se pudo obtener la IP de la instancia EC2.")
            return

        update_duckdns(
            message, config.client.duckdns_domain, config.client.duckdns_token, ip
        )

        message.reply("IP actualizada con exito.")

    except Exception as e:
        message.reply(str(e))
