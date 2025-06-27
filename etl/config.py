import logging
import os
from typing import Any, Dict, List

from airflow.models import Variable
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

REQUIRED_ENV_VARS = [
    "CLIENT_ID",
    "CLIENT_SECRET",
    "YANDEX_TOKEN",
    "EMAIL",
    "USER_ID",
    "API_FLAG",
]

PATH_VARS = [
    "INPUT_PATH",
    "OUTPUT_PATH",
]


def load_config(required_vars: List[str], path_vars: List[str]) -> Dict[str, Any]:
    load_dotenv()

    config: Dict[str, Any] = {}
    missing_vars: List[Any] = []

    for var in required_vars + path_vars:
        value = Variable.get(var, default_var=os.environ.get(var, None))

        if not value:
            missing_vars.append(var)
        else:
            config[var] = value

    if missing_vars:
        error_msg = "Отсутствуют обязательные переменные окружения: " + ", ".join(missing_vars)
        logger.error(error_msg)
        raise EnvironmentError(error_msg)

    if "INPUT_PATH" in config and not os.path.isfile(config["INPUT_PATH"]):
        error_msg = f"Входной файл не существует: {config['INPUT_PATH']}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)

    if "OUTPUT_PATH" in config:
        output_dir = os.path.dirname(config["OUTPUT_PATH"])
        if output_dir and not os.path.isdir(output_dir):
            error_msg = f"Выходная директория не существует: {output_dir}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

    logger.info("Конфигурация успешно загружена и проверена.")

    return config
