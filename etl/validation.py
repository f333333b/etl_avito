import re
import pandas as pd
import logging
import asyncio
import random
from typing import List, Optional, Tuple

import aiohttp

from data.reference_data import autoload_allowed_values

logger = logging.getLogger(__name__)

# регулярные выражения
PATTERN_CONTACT_PHONE = re.compile(
    r'^\+?7\s?\(?[\d]{3}\)?[\s-]?[\d]{3}[\s-]?[\d]{2}[\s-]?[\d]{2}$'
)
PATTERN_ID = re.compile(r'^[\dа-яА-Яa-zA-Z,\\/\[\]\(\)\-=_]{1,100}$')
PATTERN_AVITO_ID = re.compile(r'^\d+$')

def get_duplicated_values(series: pd.Series) -> pd.Series:
    """Вспомогательная функция, которая возвращает уникальные значения, дублирующиеся в серии"""
    return series[series.duplicated()].unique()

async def check_url(session: aiohttp.ClientSession, id: str, url: str, sem: asyncio.Semaphore, delay_range=(0.2, 0.5)) -> Optional[str]:
    """Вспомогательная функция для проверки одного URL"""
    if pd.isna(url) or str(url).strip() == '':
        return None
    if not url.startswith(('http://', 'https://')):
        return f"Некорректный формат URL в строке с Id {id}: {url}"
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
    url_columns = ['VideoURL', 'VideoFilesURL', 'ImageUrls']
    total_checked = 0
    sem = asyncio.Semaphore(5)

    unique_df = df.drop_duplicates(subset=['Title'])

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        tasks = []
        for col in url_columns:
            if col not in unique_df.columns:
                continue
            if col == 'ImageUrls':
                for row_id, image_urls in unique_df[col].astype(str).items():
                    if image_urls.strip():
                        first_image_url = image_urls.split('|')[0].strip()
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

def validate_required_fields(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Функция валидации обязательных колонок: наличие, заполненность, допустимые значения, тип данных"""
    errors = []
    required_columns = [key for key, val in autoload_allowed_values.items() if val['required_parameter']]

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}")

    present_required = [col for col in required_columns if col in df.columns]

    def check_row(row: pd.Series) -> Optional[str]:
        missing = [col for col in present_required if pd.isna(row[col]) or str(row[col]).strip() == ""]
        invalid = [col for col in present_required if not pd.isna(row[col])
                   and autoload_allowed_values[col].get('allowed_values')
                   and row[col] not in autoload_allowed_values[col]['allowed_values']]
        wrong_type = [col for col in present_required if not pd.isna(row[col])
                      and autoload_allowed_values[col].get('data_type')
                      and not isinstance(row[col], autoload_allowed_values[col]['data_type'])]

        messages = []
        if missing:
            plural_missing = "заполнен" if len(missing) == 1 else "заполнены"
            messages.append(f"не {plural_missing}: {', '.join(missing)}")
        if invalid:
            messages.append(f"недопустимые значения: {', '.join(invalid)}")
        if wrong_type:
            plural_wrong_type = "колонки" if len(wrong_type) == 1 else "колонок"
            messages.append(f"неверный тип данных у {plural_wrong_type}: {', '.join(wrong_type)}")

        return f"Строка {row.name}: " + "; ".join(messages) if messages else None

    errors.extend(df.apply(check_row, axis=1).dropna().tolist())
    if len(errors) > 30:
        return False, errors[:30]
    return len(errors) == 0, errors

def validate_format_fields(df: pd.DataFrame) -> tuple[bool, List[str]]:
    """Функция валидации формата данных в соответствии с требованиями каждой колонки"""
    errors = []
    is_valid = True

    df['ContactPhone'] = df['ContactPhone'].fillna('').astype(str).str.replace(r'\.0$', '', regex=True)
    invalid_phones = df[(df['ContactPhone'] != '') & (df['ContactPhone'].str.match(PATTERN_CONTACT_PHONE, na=False) == False)]
    if not invalid_phones.empty:
        is_valid = False
        errors.append(f"Некорректные номера телефонов: {invalid_phones['ContactPhone'].tolist()}")

    ids_str = df['Id'].fillna('').astype(str)
    invalid_ids = df[(ids_str != '') & (ids_str.str.match(PATTERN_ID, na=False) == False)]
    if not invalid_ids.empty:
        is_valid = False
        errors.append(f"Некорректные Id: {invalid_ids['Id'].tolist()}")

    avito_ids = df['AvitoId'].apply(lambda x: str(int(x)) if pd.notna(x) else '')
    invalid_avito_ids = df[(avito_ids != '') & (avito_ids.str.match(PATTERN_AVITO_ID, na=False) == False)]
    if not invalid_avito_ids.empty:
        is_valid = False
        errors.append(f"Некорректные AvitoId ({len(invalid_avito_ids)}): {invalid_avito_ids['AvitoId'].tolist()}")

    return is_valid, errors

def validate_data(df: pd.DataFrame) -> tuple[bool, List[str]]:
    """Общая функция валидации данных"""
    errors = []
    is_valid = True

    valid, req_errors = validate_required_fields(df)
    errors.extend(req_errors)
    is_valid &= valid

    # валидация URL (отключена для более быстрого тестирования)
    #loop = asyncio.get_event_loop()
    #valid, url_errors = loop.run_until_complete(validate_urls(df))
    #errors.extend(url_errors)
    #is_valid &= valid

    valid, format_errors = validate_format_fields(df)
    errors.extend(format_errors)
    is_valid &= valid

    if is_valid:
        logger.info("Все проверки валидации пройдены успешно")
    else:
        logger.critical("!!! Валидация не пройдена !!!")
        for error in errors:
            logger.critical(error)

    return is_valid, errors