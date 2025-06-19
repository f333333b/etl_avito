import os
import logging
from dotenv import load_dotenv

from extract import read_excel_file
from transform import (clean_raw_data, normalize_group_by_latest, check_uniqueness, normalize_addresses,
                       unmatched_addresses, remove_invalid_dealerships, fill_missing_cities, validate_data_types,
                       normalize_columns_to_constants, validate_urls, validate_required_fields)
from load import save_to_excel
from dealerships import dealerships

def main():
    try:
        # EXTRACT
        input_path = r""
        output_path = r""
        df = read_excel_file(input_path)

        # проверка наличия соответствующих колонок
        required_columns = ['Title', 'AvitoId', 'Id', 'Make', 'Address']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            logging.error(f"В датафрейме отсутствуют обязательные столбцы: {', '.join(missing)}. Проверь исходный файл.")
            return df

        # TRANSFORM
        # удаление мусорных/пустых строк
        df = clean_raw_data(df)

        # валидация типов данных определенных столбцов
        df = validate_data_types(df)

        # проверка на уникальность значений столбцов AvitoId и Id
        ok_avitoid = check_uniqueness(df, column='AvitoId', skip_empty=True)
        ok_id = check_uniqueness(df, column='Id', skip_empty=False)

        if not ok_avitoid or not ok_id:
            raise ValueError("Нарушена уникальность AvitoId или Id")

        # нормализация строк по столбцу Title
        df = normalize_group_by_latest(df)

        # фильтрация и корректировка значений Address в соответствии со справочником городов
        df['Address'] = df.apply(lambda row: normalize_addresses(row['Address'], row['AvitoId']), axis=1)
        if unmatched_addresses:
            logging.warning(f"Не удалось нормализовать адреса ({len(unmatched_addresses)} шт.):")
            for avito_id, raw_address in unmatched_addresses:
                logging.warning(f" - AvitoId: {avito_id}, Address: {raw_address}")

        # удаление строк, нарушающих дилерство
        df = remove_invalid_dealerships(df)

        # обеспечение полного размещения техники по разрешённым адресам
        df = fill_missing_cities(df, dealerships)

        # нормализация колонок Year, Condition, Kilometrage, DisplayAreas
        df = normalize_columns_to_constants(df)

        # валидация колонок VideoURL, VideoFilesURL, проверка работоспособности URL
        df = validate_urls(df)

        # валидация заполнения обязательных колонок в зависимости от VehicleType и Type
        validate_required_fields(df)

        # LOAD

        load_dotenv()
        client_id = os.getenv('CLIENT_ID')
        client_secret = os.getenv('CLIENT_SECRET')
        user_id = os.getenv('USER_ID')

        save_to_excel(df, output_path)
        logging.info(f"Файл сохранён: {output_path}")

    except Exception as e:
        logging.exception(f"Ошибка: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()