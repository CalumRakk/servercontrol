

from pyrogram import Client, filters # type: ignore

from settings import Settings, get_settings

settings= get_settings(".env/leo.env")

app = Client(settings.session_name, api_id=settings.api_id, api_hash=settings.api_hash, workdir=str(settings.worktable),bot_token =settings.bot_token)

@app.on_message(filters.text & filters.private)
def echo(client, message):
    message.reply(message.text)

app.run()