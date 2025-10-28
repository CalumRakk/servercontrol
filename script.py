from pathlib import Path
from typing import Union

from servercontrol.config import load_config_orchestator
from servercontrol.core.client_tg import init_telegram_client
from servercontrol.core.handlers import register_handlers, register_handlers_duckdns


def main(path: Union[Path, str]):

    path = Path(path) if isinstance(path, str) else path
    config = load_config_orchestator(path)
    client = init_telegram_client(config.tg_config)
    register_handlers(client, config.lab_config)
    register_handlers_duckdns(client, config)
    print("Bot iniciado con exito")

    client.run()


if __name__ == "__main__":
    main(r".env/leo.env")
