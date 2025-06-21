import re
import pandas as pd
import requests
import logging
import time
import random
from datetime import datetime
from typing import Tuple, List, Optional

from etl.load import excel_writer

logger = logging.getLogger(__name__)

def get_duplicated_values(series: pd.Series) -> pd.Series:
    """Функция возвращает уникальные значения, которые дублируются в серии"""
    return series[series.duplicated()].unique()

def get_duplicated_rows(df: pd.DataFrame, column: str, skip_empty: bool = True) -> pd.DataFrame:
    """Функция возвращает строки, содержащие дублирующиеся значения в заданной колонке"""
    series = df[column].dropna() if skip_empty else df[column]
    duplicates = get_duplicated_values(series)
    return df[df[column].isin(duplicates)]

def save_duplicates_to_excel(df: pd.DataFrame, column: str) -> str:
    """Функция сохраняет дубликаты в Excel-файл и возвращает путь к файлу"""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"./validation_logs/duplicates_{column}_{timestamp}.xlsx"
    with excel_writer(filename) as fname:
        df.to_excel(fname, index=False)
    return filename

def validate_uniqueness(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Функция валидации уникальности колонок AvitoId и Id"""
    errors = []
    for column, skip_empty in [('AvitoId', True), ('Id', False)]:
        duplicated_df = get_duplicated_rows(df, column, skip_empty)
        if not duplicated_df.empty:
            file_path = save_duplicates_to_excel(duplicated_df, column)
            errors.append(
                f"Найдены дубликаты в '{column}' (всего: {duplicated_df[column].nunique()}). Сохранено в: {file_path}"
            )
        else:
            logger.info(f"Проверка '{column}' на уникальность пройдена")
    return len(errors) == 0, errors

def check_url(session: requests.Session, id: str, url: str, delay_range=(0.2, 0.5)) -> Optional[str]:
    '''Функция для проверки одного URL'''
    if pd.isna(url) or str(url).strip() == '':
        return None
    if not url.startswith(('http://', 'https://')):
        return f"Некорректный формат URL в строке с Id {id}: {url}"
    try:
        time.sleep(random.uniform(*delay_range))
        response = session.head(url, timeout=5, allow_redirects=True)
        if response.status_code != 200:
            return f"URL {url} в строке с Id {id} вернул статус {response.status_code}"
    except requests.RequestException as e:
        return f"Ошибка при HEAD-запросе к {url} в строке с Id {id}: {e}"
    return None

def validate_urls(df: pd.DataFrame) -> Tuple[bool, List[str]]:
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
    with requests.Session() as session:
        session.headers.update(HEADERS)
        for col in url_columns:
            if col not in df.columns:
                logger.warning(f"Колонка {col} отсутствует, проверка пропущена")
                continue
            if col == 'ImageUrls':
                for row_id, image_urls in df[col].astype(str).items():
                    if image_urls.strip():
                        first_image_url = image_urls.split('|')[0]
                        total_checked += 1
                        check_result = check_url(session=session, id=row_id, url=first_image_url.strip())
                        if check_result:
                            errors.append(check_result)
            else:
                for row_id, url in df[col].items():
                    total_checked += 1
                    check_result = check_url(session=session, id=row_id, url=url)
                    if check_result:
                        errors.append(check_result)
    if not errors:
        logger.info("Проверка URL пройдена успешно")
    logger.info(f"Всего URL проверено: {total_checked}, найдено ошибок: {len(errors)}")
    return len(errors) == 0, errors

def validate_required_fields(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Функция валидации заполнения обязательных колонок"""
    errors = []
    base_columns = ['Id', 'Address', 'Category', 'Title', 'Description', 'VehicleType', 'Make', 'Model',
                    'Type', 'Year', 'Availability', 'Condition']
    moto_columns = ['EngineType', 'Power', 'EngineCapacity', 'Kilometrage']
    quadro_columns = moto_columns + ['PersonCapacity']
    boat_engines_columns = ['EngineType', 'Power']
    boats_columns = ['FloorType', 'Length', 'Width', 'SeatingCapacity', 'MaxPower', 'TrailerIncluded', 'EngineIncluded']
    missing_columns = [col for col in base_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}")

    def check_row(row):
        missing = []
        for col in base_columns:
            val = row.get(col)
            if pd.isna(val) or str(val).strip() == "":
                missing.append(col)
        vt = row.get("VehicleType")
        tp = row.get("Type")
        additional = []
        if vt in ["Мопеды и скутеры", "Мотоциклы"]:
            additional = moto_columns
        elif vt == "Квадроциклы":
            additional = quadro_columns
        elif vt == "Моторные лодки и моторы":
            if tp == "Лодочный мотор":
                additional = boat_engines_columns
            elif tp in ["Лодка ПВХ (надувная)", "Лодка RIB (комбинированная)", "Лодка с жестким корпусом"]:
                additional = boats_columns
        for col in additional:
            val = row.get(col)
            if pd.isna(val) or str(val).strip() == "":
                missing.append(col)
        image_urls_empty = pd.isna(row.get("ImageUrls")) or str(row["ImageUrls"]).strip() == ""
        image_names_empty = pd.isna(row.get("ImageNames")) or str(row["ImageNames"]).strip() == ""
        if image_urls_empty and image_names_empty:
            missing.append("ImageUrls or ImageNames")
        if missing:
            return f"Строка {row.name}: пропущены обязательные поля: {', '.join(missing)}"
        return None

    row_errors = df.apply(check_row, axis=1).dropna().tolist()
    errors.extend(row_errors)

    if not errors:
        logger.info("Проверка обязательных полей пройдена")
    return len(errors) == 0, errors

def validate_format_fields(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    errors = []
    is_valid = True

    if 'EMail' in df.columns:
        invalid_emails = df[~df['EMail'].fillna('').astype(str).str.match(r"[^@]+@[^@]+\.[^@]+")]
        if not invalid_emails.empty:
            is_valid = False
            errors.append(f"Некорректные email: {len(invalid_emails)} строк")

    if 'ContactPhone' in df.columns:
        invalid_phones = df[~df['ContactPhone'].fillna('').astype(str).str.fullmatch(r"7\d{10}")]
        if not invalid_phones.empty:
            is_valid = False
            errors.append(f"Некорректные номера телефонов: {len(invalid_phones)} строк")

    if 'Id' in df.columns:
        invalid_ids = df[~df['Id'].fillna('').astype(str).str.fullmatch(r"[A-Za-z0-9]+")]
        if not invalid_ids.empty:
            is_valid = False
            errors.append(f"Некорректные Id: {len(invalid_ids)} строк")

    if 'AvitoId' in df.columns:
        invalid_avito_ids = df[~df['AvitoId'].fillna('').astype(str).str.fullmatch(r"\d+")]
        if not invalid_avito_ids.empty:
            is_valid = False
            errors.append(f"Некорректные AvitoId: {len(invalid_avito_ids)} строк")

    return is_valid, errors

def validate_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """Общая функция валидации данных"""
    errors = []
    is_valid = True

    # валидация уникальности
    valid, uniq_errors = validate_uniqueness(df)
    errors.extend(uniq_errors)
    is_valid &= valid

    # валидация обязательных полей
    valid, req_errors = validate_required_fields(df)
    errors.extend(req_errors)
    is_valid &= valid

    # валидация URL
    # отключена потому что нужно проработать, как обойти ограничение авито на частые запросы (to do)
    #valid, url_errors = validate_urls(df)
    #errors.extend(url_errors)
    #is_valid &= valid

    # валидация форматов
    valid, format_errors = validate_format_fields(df)
    errors.extend(format_errors)
    is_valid &= valid

    if is_valid:
        logger.info("Все проверки валидации пройдены успешно")
    else:
        logger.error(f"Валидация не пройдена: {'; '.join(errors)}")

    return is_valid, errors
