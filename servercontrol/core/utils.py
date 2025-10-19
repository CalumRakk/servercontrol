
from labcontrol.config import Config as LabConfig


def should_wait_get_params(config: LabConfig)-> bool:
    if not config.vocareum_cookies_path.exists() or not config.lab_cookies_path.exists():
        return True
    return False