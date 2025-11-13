from pyrogram import Client, filters  # type: ignore
from pyrogram.handlers import MessageHandler  # type: ignore

from servercontrol.config import ManagerConfig

from .commands_academy import (
    end_aws,
    get_aws,
    get_aws_sso,
    get_aws_status,
    help,
    start_aws,
    update_ip,
)


def register_handlers(app: Client, config: ManagerConfig): # <-- Cambiar firma para recibir ManagerConfig

    # app.add_handler(MessageHandler(echo, filters.text & filters.private))
    app.add_handler(
        MessageHandler(
            lambda client, message: get_aws_status(client, message, config.lab_config),
            filters.command("pc_status"),
        )
    )
    app.add_handler(
        MessageHandler(
            lambda client, message: start_aws(client, message, config.lab_config),
            filters.command("pc_start") & filters.private,
        )
    )
    app.add_handler(
        MessageHandler(
            lambda client, message: end_aws(client, message, config.lab_config),
            filters.command("pc_end") & filters.private,
        )
    )
    app.add_handler(
        MessageHandler(
            lambda client, message: get_aws(client, message, config.lab_config),
            filters.command("pc_details") & filters.private,
        )
    )
    app.add_handler(
        MessageHandler(
            lambda client, message: get_aws_sso(client, message, config.lab_config),
            filters.command("pc_sso") & filters.private,
        )
    )

    # --- REGISTRO DEL NUEVO COMANDO ---
    app.add_handler(
        MessageHandler(
            lambda client, message: update_ip(client, message, config),
            filters.command("update_ip") & filters.private,
        )
    )
    
    app.add_handler(MessageHandler(help, filters.command("help")))