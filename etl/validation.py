from __future__ import annotations

import asyncio
import logging
import random
from datetime import datetime
from typing import Any, Dict, List, Optional, Pattern, Tuple, Type

import aiohttp
import pandas as pd

from etl.data.reference_data import autoload_allowed_values

logger = logging.getLogger(__name__)


def get_duplicated_values(series: pd.Series) -> pd.Series:
    """Вспомогательная функция, которая возвращает уникальные значения, дублирующиеся в серии"""
    return series[series.duplicated()].unique()


async def check_url(
    session: aiohttp.ClientSession,
    id: str,
    url: str,
    sem: asyncio.Semaphore,
    delay_range=(0.2, 0.5),
) -> Optional[str]:
    """Вспомогательная функция для проверки одного URL"""
    if pd.isna(url) or str(url).strip() == "":
        return None
    async with sem:
        try:
            await asyncio.sleep(random.uniform(*delay_range))
            async with session.head(url, timeout=5, allow_redirects=True) as response:
                if response.status != 200:
                    return f"URL {url} в строке с Id {id} вернул статус {response.status}"
        except Exception as e:
            return f"Ошибка при HEAD-запросе к {url} в строке с Id {id}: {e}"
    return None


async def validate_urls(df: pd.DataFrame) -> tuple[bool, List[str]]:
    """Функция валидации значений колонок VideoURL и VideoFilesURL"""
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/123.0.0.0 Safari/537.36"
        )
    }
    errors = []
    url_columns = ["VideoURL", "VideoFilesURL", "ImageUrls"]
    total_checked = 0
    sem = asyncio.Semaphore(5)

    unique_df = df.drop_duplicates(subset=["Title"])

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = []
        for col in url_columns:
            if col not in unique_df.columns:
                continue
            if col == "ImageUrls":
                for row_id, image_urls in unique_df[col].astype(str).items():
                    if image_urls.strip():
                        first_image_url = image_urls.split("|")[0].strip()
                        total_checked += 1
                        tasks.append(check_url(session, str(row_id), first_image_url, sem))
                        await asyncio.sleep(2)
            else:
                for row_id, url in unique_df[col].items():
                    total_checked += 1
                    tasks.append(check_url(session, str(row_id), url, sem))
        results = await asyncio.gather(*tasks)
        errors.extend(result for result in results if result)

    if not errors:
        logger.info("Проверка URL пройдена успешно")
    logger.info(f"Всего URL проверено: {total_checked}, найдено ошибок: {len(errors)}")
    return len(errors) == 0, errors


# вспомогательные функции для этапа валидации обязательных колонок
def is_missing(val: Any) -> bool:
    return pd.isna(val) or str(val).strip() == ""


def is_correct_type(val: Any | None, expected_type: Type | None) -> bool:
    if expected_type is None:
        return True
    if expected_type == int:
        return pd.api.types.is_integer(val)
    if expected_type == float:
        return pd.api.types.is_float(val)
    if expected_type == str:
        return isinstance(val, str)
    if expected_type == datetime:
        return isinstance(val, datetime)
    return False


def is_allowed_value(val: Any | None, allowed_values: List[str | int] | None) -> bool:
    if allowed_values is None:
        return True
    try:
        return val in allowed_values
    except TypeError:
        return False


def matches_pattern(val: Any | None, pattern: Pattern | None) -> bool:
    if pattern is None or not isinstance(val, str):
        return True
    return bool(pattern.match(val.strip()))


def is_within_range(val: Any | None, min_value: int, max_value: int | None) -> bool:
    if isinstance(val, (int, float)):
        if min_value is not None and val < min_value:
            return False
        if max_value is not None and val > max_value:
            return False
    return True


def validate_required_fields(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Функция валидации обязательных колонок:
    наличие, заполненность, допустимые значения, тип данных
    """
    errors: List[str] = []

    required_columns = [
        key for key, val in autoload_allowed_values.items() if val["required_parameter"]
    ]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}")

    present_required = [col for col in required_columns if col in df.columns]
    if not present_required:
        return False, errors

    def check_row(row: pd.Series) -> Optional[str]:
        row_errors: List[str] = []
        for col in present_required:
            val = row[col]
            rule: Dict[str, Any] = autoload_allowed_values[col]

            if is_missing(val):
                row_errors.append(f"{col} — не заполнено")
                continue

            if not is_correct_type(val, rule.get("data_type")):
                row_errors.append(f"{col} — неверный тип данных")
                continue

            if not is_within_range(val, rule.get("min_value"), rule.get("max_value")):
                row_errors.append(
                    f"{col} — выходит за допустимые пределы "
                    f"({rule.get('min_value')} - {rule.get('max_value')})"
                )

            if rule.get("data_type") == str and not is_allowed_value(
                val, rule.get("allowed_values")
            ):
                row_errors.append(f"{col} — недопустимое значение")

            if not matches_pattern(val, rule.get("pattern")):
                row_errors.append(f"{col} — не соответствует формату")

        return f"Строка {row.name}: " + "; ".join(row_errors) if row_errors else None

    row_errors = df.apply(check_row, axis=1).dropna().tolist()
    errors.extend(row_errors)

    return (False, errors[:30]) if errors else (True, [])


def validate_data(df: pd.DataFrame) -> tuple[bool, List[str]]:
    """Общая функция валидации данных"""
    errors = []
    is_valid = True

    valid, req_errors = validate_required_fields(df)
    errors.extend(req_errors)
    is_valid &= valid

    # валидация URL (отключена для более быстрого тестирования)
    # loop = asyncio.get_event_loop()
    # valid, url_errors = loop.run_until_complete(validate_urls(df))
    # errors.extend(url_errors)
    # is_valid &= valid

    # valid, format_errors = validate_format_fields(df)
    # errors.extend(format_errors)
    # is_valid &= valid

    if is_valid:
        logger.info("Все проверки валидации пройдены успешно")
    else:
        logger.critical("!!! Валидация не пройдена !!!")
        for error in errors:
            logger.critical(error)

    return is_valid, errors
