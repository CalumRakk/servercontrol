import asyncio
from pathlib import Path
from typing import Union

from servercontrol.config import load_config_orchestator
from servercontrol.discord.client import init_discord_client
from servercontrol.discord.handlers import register_handlers_discord


async def main(path: Union[Path, str]):

    path = Path(path) if isinstance(path, str) else path
    config = load_config_orchestator(path)

    platform = config.orchestrator_config.bot_platform
    tasks = []


    # if platform in ["telegram", "both"]:
    #     print("Configurando bot de Telegram...")
    #     tg_client = init_telegram_client(config.tg_config)
    #     register_handlers(tg_client, config)
    #     tasks.append(tg_client.start())
    #     print("Bot de Telegram configurado.")

    if platform in ["discord", "both"]:
        print("Configurando bot de Discord...")
        discord_bot = init_discord_client(config.discord_config)
        register_handlers_discord(discord_bot, config)
        tasks.append(discord_bot.start(config.discord_config.bot_token))
        print("Bot de Discord configurado.")
    
    if not tasks:
        print("No se ha seleccionado ninguna plataforma de bot para ejecutar. Cerrando.")
        return

    print(f"Iniciando bot(s) para la plataforma: '{platform}'...")
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main(r".env/leo.env"))
    except KeyboardInterrupt:
        print("\nCerrando bots...")