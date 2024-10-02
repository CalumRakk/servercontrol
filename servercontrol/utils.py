import logging
import time

logging.basicConfig(
    filename="log.txt",
    filemode="a",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%d-%m-%Y %I:%M:%S %p",
    level=logging.INFO,
    encoding="utf-8",
)

logger = logging.getLogger(__name__)


def log_decorator(func):
    def wrapper(*args, **kwargs):
        logger.info(
            f"Llamando a {func.__name__} con los argumentos: {args}, kwargs: {kwargs}"
        )
        result = func(*args, **kwargs)
        logger.info(f"{func.__name__} devuelve {result}")
        return result

    return wrapper


def seconds_to_timeh(seconds):
    horas = seconds // 3600
    minutos = (seconds % 3600) // 60
    segundos = (seconds % 3600) % 60

    horasString = str(horas).zfill(2)
    minutosString = str(minutos).zfill(2)
    segundosString = str(segundos).zfill(2)

    return f"{horasString}:{minutosString}:{segundosString}"


def sleep_program(sleep_seconds: int):
    if sleep_seconds > 0:
        logger.info(
            f"El programa entro en modo sueño: {seconds_to_timeh(sleep_seconds)}"
        )

    while sleep_seconds > 0:
        print(f"Tiempo restante: {seconds_to_timeh(sleep_seconds)}", end="\r")

        sleep_seconds -= 1
        time.sleep(1)
