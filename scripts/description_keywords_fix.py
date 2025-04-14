"""
Скрипт для замены части описания объявлений в Excel-файле в формате HTML на основе типа транспорта (VehicleType)
Использует json-файл с ключевыми блоками текста, соответствующими каждому типу
"""

import pandas as pd
import argparse
import logging
import json
import os

logging.basicConfig(level=logging.INFO, format="%(message)s")

def process_cell(df, key_dict, avito_id, description, vehicle_type):
    '''Функция обработки ячейки'''
    if pd.isna(avito_id) or pd.isna(description):
        return 0

    try:
        current = df.loc[df['AvitoId'] == int(avito_id), 'Description'].dropna().values
        if not current or not isinstance(current[0], str):
            return 0
        parts = list(current[0].partition(key_dict['full']))
        if not parts[1]:
            return 0
        parts[1] = key_dict.get(vehicle_type, '')
        updated = ''.join(parts)
        df.loc[df['AvitoId'] == int(avito_id), 'Description'] = updated
        return 1
    except Exception as e:
        logging.warning(f"Ошибка при обработке ID {avito_id}: {e}")
        return 0

def main(input_path, output_path):
    if not os.path.exists(input_path):
        logging.error(f"Файл не найден: {input_path}")
        return

    with open("vehicle_keywords.json", "r", encoding="utf-8") as f:
        key_dict = json.load(f)

    df = pd.read_excel(input_path)
    processed = 0

    records = zip(df['AvitoId'].tolist(), df['Description'].tolist(), df['VehicleType'].tolist())
    total = len(df)
    logging.info(f'Всего объявлений: {total}')

    for avito_id, desc, vehicle_type in records:
        processed += process_cell(df, key_dict, avito_id, desc, vehicle_type)

    df.to_excel(output_path, index=False)
    logging.info(f'Готово. Обработано {processed} из {total}. Результат сохранён в: {output_path}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Заменяет HTML-блоки описания в Excel-файле Avito.")
    parser.add_argument('--input', required=True, help='Путь к исходному Excel-файлу')
    parser.add_argument('--output', required=True, help='Путь к результирующему Excel-файлу')
    args = parser.parse_args()
    main(args.input, args.output)