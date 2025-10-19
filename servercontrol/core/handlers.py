from pyrogram import Client, filters  # type: ignore
from pyrogram.handlers import MessageHandler  # type: ignore

from .commands import echo


def register_handlers(app: Client): 

    app.add_handler(MessageHandler(echo, filters.text & filters.private))
        