from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def ensure_file_exists(path: str) -> None:
    """Функция проверки существования файла"""
    if not isinstance(path, str):
        raise TypeError(f"Ожидалась строка, получено: {type(path).__name__}")
    if not os.path.isfile(path):
        logger.error(f"Файл не найден: {path}")
        raise FileNotFoundError(f"Файл не найден: {path}")


def ensure_dir_created(path: str) -> None:
    """Функция проверки существования папки. При отсутствии создает папку"""
    if not isinstance(path, str):
        raise TypeError(f"Ожидалась строка, получено: {type(path).__name__}")
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)
        logger.info(f"Папка {path} создана.")
