import re
import pandas as pd
import logging
import requests
from datetime import datetime
from dealerships import cities, dealerships, city_to_full_address

unmatched_addresses = set()
id_counter = 1

def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """Функция для удаления мусорных/пустых строк"""

    # стрип строковых ячеек
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # удаление полностью пустых строк
    df_cleaned = df.dropna(how='all')

    # удаление дублей по столбцам
    df_cleaned = df_cleaned.drop_duplicates(subset=['AvitoId', 'Id'])

    # подсчет количества удаленных строк
    removed = len(df) - len(df_cleaned)
    logging.info(f'Удалено мусорных/пустых строк: {removed}')

    return df_cleaned

def check_uniqueness(df: pd.DataFrame, column: str, skip_empty: bool) -> bool:
    """
    Функция проверки уникальности строк по столбцу.
    Если skip_empty=True — пропускает пустые значения (например, для AvitoId).
    Если skip_empty=False — считает все значения, включая пустые (например, для Id).
    Возвращает True, если всё ок.
    Возвращает False и логирует ошибку, если найдены дубликаты
    """

    if skip_empty:
        filled_ids = df[column].dropna()
    else:
        filled_ids = df[column]

    duplicated = filled_ids[filled_ids.duplicated()].unique()

    if len(duplicated) > 0:
        filename = f"duplicates_{column}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
        df[df[column].isin(duplicated)].to_excel(filename, index=False)
        logging.error(f"Найдены дубликаты в '{column}' (всего: {len(duplicated)}). Сохранено в: {filename}")
        return False

    logging.info(f"Проверка '{column}' на уникальность успешно пройдена, дубликатов нет")
    return True

def normalize_group(group: pd.DataFrame, columns_to_normalize: list) -> pd.DataFrame:
    if group['AvitoDateEnd'].notna().any():
        idx = group['AvitoDateEnd'].idxmax()
    else:
        idx = group.index[0]
    ref_row = group.loc[idx, columns_to_normalize]
    for col in columns_to_normalize:
        group[col] = ref_row[col]
    return group

def normalize_group_by_latest(df: pd.DataFrame) -> pd.DataFrame:
    exclude_cols = ['AvitoStatus', 'AvitoDateEnd', 'Address']
    cols_to_normalize = [col for col in df.columns if col not in exclude_cols]
    df['AvitoDateEnd'] = pd.to_datetime(df['AvitoDateEnd'], errors='coerce', utc=True)
    normalized_df = df.groupby('Title', group_keys=False).apply(
        lambda group: normalize_group(group, cols_to_normalize)
    ).reset_index(drop=True)
    logging.info(f"Количество нормализованных строк по столбцу 'Title': {normalized_df.shape[0]}.")
    normalized_df['AvitoDateEnd'] = normalized_df['AvitoDateEnd'].dt.tz_localize(None).dt.strftime("%Y-%m-%d")
    return normalized_df

def normalize_addresses(raw_address: str, id: str) -> str:
    """Функция для нормализации написания адресов в столбце Address"""
    for city, full_address in city_to_full_address.items():
        if re.search(fr"\b{re.escape(city)}\b", raw_address, re.IGNORECASE):
            return full_address
    unmatched_addresses.add((id, raw_address))
    return raw_address

def remove_invalid_dealerships(df: pd.DataFrame) -> pd.DataFrame:
    """
    Функция удаления строк, нарушающих дилерство по брендам и городам.
    Логирует AvitoId удалённых строк.
    """
    invalid_ids = []
    def is_allowed(row):
        brand = str(row['Make']).strip()
        address = str(row['Address']).strip()
        allowed_cities = dealerships.get(brand)
        if allowed_cities is None:
            return True
        for city in allowed_cities:
            if city.lower() in address.lower():
                return True
        invalid_ids.append(row['AvitoId'])
        return False
    result_df = df[df.apply(is_allowed, axis=1)]
    if invalid_ids:
        logging.info(f"Удалены строки с нарушением дилерства: {len(invalid_ids)} шт.")
        invalid_list = [int(avito_id) for avito_id in invalid_ids]
        logging.info(f"Список AvitoId удаленных строк:\n{invalid_list}")
    else:
        logging.info("Нарушений дилерства не обнаружено.")
    return result_df


def fill_missing_cities(df: pd.DataFrame, dealerships: dict) -> pd.DataFrame:
    """
    Валидация по каждой паре Title + Make: размещён ли товар во всех нужных городах.
    Если нет — добавляем недостающие строки.
    """
    global id_counter
    new_rows = []
    for (title, make), group in df.groupby(['Title', 'Make']):
        allowed_cities = dealerships.get(make, cities)
        source = "списка дилерства" if make in dealerships else "общего списка городов"
        existing_cities = set()
        for _, row in group.iterrows():
            if str(row['AvitoStatus']).strip().lower() != 'активно':
                continue
            address = str(row['Address'])
            for city in allowed_cities:
                if city.lower() in address.lower():
                    existing_cities.add(city)
                    break
        missing_cities = set(allowed_cities) - existing_cities
        if missing_cities:
            template_row = group.iloc[0].copy()
            for city in sorted(missing_cities):
                new_row = template_row.copy()
                new_row['Address'] = f"{city}"
                new_row['AvitoId'] = ''
                new_row['AvitoDateEnd'] = ''
                new_row['AvitoStatus'] = 'Активно'
                new_row['Id'] = f"{datetime.now().strftime('%d%m%Y')}{id_counter:06d}"
                id_counter += 1
                new_rows.append(new_row)
            logging.info(f"Объявление '{title}': добавлены строки в количестве {len(missing_cities)} шт.")
    if new_rows:
        df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
        logging.info(f"Всего добавлено строк: {len(new_rows)}")
    else:
        logging.info("Все товары размещены в нужных городах. Новые строки не добавлялись.")
    return df

def normalize_columns_to_constants(df: pd.DataFrame) -> pd.DataFrame:
    """Функция нормализации колонок Condition, Year, Kilometrage, DisplayAreas - приведение к единым значениям"""

    current_year = datetime.now().year
    df.loc[df['Condition'] != 'Б/у', 'Condition'] = 'Б/у'
    df.loc[df['Year'] != current_year, 'Year'] = current_year
    df.loc[df['Kilometrage'] != 5, 'Kilometrage'] = 5
    df.loc[df['DisplayAreas'] != '', 'DisplayAreas'] = ''
    return df


def validate_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Функция валидации типов данных определенных колонок"""

    numeric_columns = ["AvitoId", "Price", "EngineCapacity", "Kilometrage", "PersonCapacity", "SeatingCapacity",
                       "MaxPower", "Stroke", "TrackWidth"]
    string_columns = ["Id", "AvitoStatus", "AvitoDateEnd", "ListingFee", "Category", "Title",
                      "Description", "Condition", "Price", "ImageUrls", "VideoUrl", "Address", "ManagerName",
                      "EMail", "ContactPhone", "ContactMethod", "Availability", "CompanyName", "Control",
                      "Cylinders", "CylindersPosition", "DisplayAreas", "DriveType",
                      "EngineCooling", "EngineIncluded", "EngineMake", "EngineType", "EngineWeight",
                      "EngineYear", "FloorType", "FuelFeed", "Length", "Make",
                      "Model", "MotoType", "NumberOfGears", "Owners", "ShaftLength", "StartingSystem",
                      "TechnicalPassport",
                      "TrailerIncluded", "Transmission", "TransomHeight", "Type", "VehicleType",
                      "VIN", "Weight", "Width"]
    existing_numeric_columns = [col for col in numeric_columns if col in df.columns]
    existing_string_columns = [col for col in string_columns if col in df.columns]
    try:
        for col in existing_numeric_columns:
            if not pd.api.types.is_integer_dtype(df[col]):
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
    except Exception as e:
        logging.error(f'Ошибка при приведении колонки {col} к типу int: {e}')
    try:
        for col in existing_string_columns:
            if not pd.api.types.is_string_dtype(df[col]):
                df[col] = df[col].astype('string')
    except Exception as e:
        logging.error(f'Ошибка при приведении колонки {col} к типу string: {e}')
    return df

def validate_urls(df: pd.DataFrame) -> pd.DataFrame:
    """Функция валидации значений колонок VideoURL и VideoFilesURL, а также проверки URL"""

    url_columns = ['VideoURL', 'VideoFilesURL']
    for col in url_columns:
        if col not in df.columns:
            logging.error(f'Колонка {col} отсутствует')
            continue
        for url in df[col].astype(str):
            if not url.startswith(('http://', 'https://')):
                logging.warning(f'Некорректный формат URL в колонке {col}: {url}')
                continue
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code != 200:
                    logging.warning(f'URL {url} в колонке {col} вернул статус {response.status_code}')
            except Exception as e:
                logging.warning(f'Ошибка при HEAD-запросе к {url} в колонке {col}: {e}')
    return df

def validate_required_fields(df: pd.DataFrame) -> None:
    """Функция валидации заполнения обязательных колонок в зависимости от VehicleType и Type"""

    base_columns = ['Id', 'Address', 'Category', 'Title', 'Description', 'VehicleType', 'Make', 'Model',
                    'Type', 'Year', 'Availability', 'Condition']
    moto_columns = ['EngineType', 'Power', 'EngineCapacity', 'Kilometrage']
    quadro_columns = moto_columns + ['PersonCapacity']
    boat_engines_columns = ['EngineType', 'Power']
    boats_columns = ['FloorType', 'Length', 'Width', 'SeatingCapacity', 'MaxPower', 'TrailerIncluded', 'EngineIncluded']

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
            logging.error(f"Строка {row.name}: пропущены обязательные поля: {', '.join(missing)}")
    df.apply(check_row, axis=1)