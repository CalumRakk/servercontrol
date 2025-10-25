from labcontrol.config import Config as LabConfig
from pyrogram import Client, filters  # type: ignore
from pyrogram.handlers import MessageHandler  # type: ignore

from .commands import end_aws, get_aws_status, help, start_aws


def register_handlers(app: Client, config: LabConfig): 

    # app.add_handler(MessageHandler(echo, filters.text & filters.private))
    app.add_handler(MessageHandler(lambda client, message: get_aws_status(client, message, config), filters.command("status") & filters.private))
    app.add_handler(MessageHandler(lambda client, message: start_aws(client, message, config), filters.command("start") & filters.private))
    app.add_handler(MessageHandler(lambda client, message: end_aws(client, message, config), filters.command("end") & filters.private))
    # app.add_handler(MessageHandler(lambda client, message: get_aws(client, message, config), filters.command("content") & filters.private))
    app.add_handler(MessageHandler(help, filters.command("help") & filters.private))