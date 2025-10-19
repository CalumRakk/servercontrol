from pyrogram import Client, filters  # type: ignore


def register_handlers(app: Client):
    @app.on_message(filters.text & filters.private)
    def echo(client, message):
        message.reply(message.text)
        