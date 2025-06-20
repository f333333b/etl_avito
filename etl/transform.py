import re
import pandas as pd
import logging
from datetime import datetime
from etl.dealerships import cities, dealerships, city_to_full_address

def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """Функция для удаления мусорных/пустых строк"""

    # стрип строковых ячеек
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)

    # удаление полностью пустых строк
    df_cleaned = df.dropna(how='all')

    # удаление дублей по колонкам
    df_cleaned = df_cleaned.drop_duplicates(subset=['AvitoId', 'Id'])

    # подсчет количества удаленных строк
    removed = len(df) - len(df_cleaned)
    logging.info(f'Удалено мусорных/пустых строк: {removed}')

    return df_cleaned

def normalize_group_by_latest(df: pd.DataFrame) -> pd.DataFrame:
    """Функция для нормализации строк, сгруппированных по Title"""
    exclude_cols = ['AvitoStatus', 'AvitoDateEnd', 'Address']
    cols_to_normalize = [col for col in df.columns if col not in exclude_cols]
    df['AvitoDateEnd'] = pd.to_datetime(df['AvitoDateEnd'], errors='coerce', utc=True)
    normalized_df = df.groupby('Title', group_keys=False).apply(
        lambda group: normalize_group(group, cols_to_normalize)
    ).reset_index(drop=True)
    logging.info(f"Количество нормализованных строк по колонке 'Title': {normalized_df.shape[0]}.")
    normalized_df['AvitoDateEnd'] = normalized_df['AvitoDateEnd'].dt.tz_localize(None).dt.strftime("%Y-%m-%d")
    return normalized_df

def normalize_addresses(raw_address: str, id: str) -> str:
    """Функция для нормализации написания адресов в колонке Address"""
    for city, full_address in city_to_full_address.items():
        if re.search(fr"\b{re.escape(city)}\b", raw_address, re.IGNORECASE):
            return full_address
    logging.warning(f"Ненормализованный адрес (AvitoId: {id}): {raw_address}")
    return raw_address

def remove_invalid_dealerships(df: pd.DataFrame) -> pd.DataFrame:
    """Функция удаления строк, нарушающих дилерство по брендам и городам"""
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
    """Функция валидации размещения по всем городам согласно Title и Make"""
    id_counter = 1
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
    df['DisplayAreas'] = df['DisplayAreas'].astype(str)
    df.loc[df['DisplayAreas'] != '', 'DisplayAreas'] = ''
    return df

def normalize_addresses_column(df: pd.DataFrame) -> pd.DataFrame:
    df['Address'] = df.apply(lambda row: normalize_addresses(row['Address'], row['AvitoId']), axis=1)
    return df

def normalize_group(group: pd.DataFrame, columns_to_normalize: list) -> pd.DataFrame:
    if group['AvitoDateEnd'].notna().any():
        idx = group['AvitoDateEnd'].idxmax()
    else:
        idx = group.index[0]
    ref_row = group.loc[idx, columns_to_normalize]
    for col in columns_to_normalize:
        group[col] = ref_row[col]
    return group

def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
    """Функция приведения типов данных определённых колонок"""
    df = df.copy()
    numeric_columns = [
        "AvitoId", "Price", "EngineCapacity", "Kilometrage", "PersonCapacity",
        "SeatingCapacity", "MaxPower", "Stroke", "TrackWidth"
    ]
    string_columns = [
        "Id", "AvitoStatus", "AvitoDateEnd", "ListingFee", "Category", "Title",
        "Description", "Condition", "ImageUrls", "VideoUrl", "Address", "ManagerName",
        "EMail", "ContactPhone", "ContactMethod", "Availability", "CompanyName", "Control",
        "Cylinders", "CylindersPosition", "DisplayAreas", "DriveType",
        "EngineCooling", "EngineIncluded", "EngineMake", "EngineType", "EngineWeight",
        "EngineYear", "FloorType", "FuelFeed", "Length", "Make",
        "Model", "MotoType", "NumberOfGears", "Owners", "ShaftLength", "StartingSystem",
        "TechnicalPassport", "TrailerIncluded", "Transmission", "TransomHeight", "Type",
        "VehicleType", "VIN", "Weight", "Width"
    ]
    existing_numeric_columns = [col for col in numeric_columns if col in df.columns]
    existing_string_columns = [col for col in string_columns if col in df.columns]
    errors = []
    for col in existing_numeric_columns:
        try:
            if not pd.api.types.is_integer_dtype(df[col]):
                df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
        except Exception as e:
            errors.append(f"Ошибка при приведении колонки {col} к типу int: {e}")
            logging.error(errors[-1])
    for col in existing_string_columns:
        try:
            if not pd.api.types.is_string_dtype(df[col]):
                df[col] = df[col].astype('string')
        except Exception as e:
            errors.append(f"Ошибка при приведении колонки {col} к типу string: {e}")
            logging.error(errors[-1])
    if errors:
        logging.warning(f"Обнаружено {len(errors)} ошибок при приведении типов. См. логи выше.")
    return df