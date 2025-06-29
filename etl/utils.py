from __future__ import annotations

import logging
import os
from functools import wraps

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

def safe_transform(func):
    """Декоратор для безопасного выполнения трансформаций датафрейма"""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError as e:
            logger.error(f"Ошибка в {func.__name__}: отсутствует колонка {e}")
            raise
        except Exception as e:
            logger.error(f"Неизвестная ошибка в {func.__name__}: {e}")
            raise

    return wrapper