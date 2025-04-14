'''Скрипт для сверки адресов объявлений в Excel-файле'''

from dotenv import load_dotenv
import os
import sys
import argparse
import pandas as pd
from datetime import datetime

from freeze_1st_row import freeze_1st_row
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config.addresses_map import address_map

load_dotenv()

# обработка аргументов
parser = argparse.ArgumentParser(description="Сверка адресов объявлений в Excel-файле")
parser.add_argument('--input', required=True)
args = parser.parse_args()

# переменные и обработка путей
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
file_path = os.path.join(desktop_path, args.input)

addresses = address_map
df = pd.read_excel(file_path)

timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
total = len(df)
valid = 0
invalid = 0
processed = 0
unmatched = 0

if 'Address' not in df.columns:
    raise ValueError("В таблице отсутствует колонка 'Address'")

for index, row in df.iterrows():
    if row['Address'] in addresses.values():
        valid += 1
    else:
        invalid += 1
        matched = False

        for city in addresses:
            if city in row['Address'].lower():
                df.at[index, "Address"] = address_map[city]
                processed += 1
                matched = True
                break
        if not matched:
            unmatched += 1
            print(f"Не удалось изменить адрес: {row['Address']}")

# сохранение
output_file = os.path.join(desktop_path, f"file_updated_{timestamp}.xlsx")
df.to_excel(output_file, index=False)

# заморозка первой строки
freeze_1st_row(output_file)

print('Обработка завершена')
print(f"Файл сохранён: {output_file}")
print(f'Всего объявлений в таблице: {total}')
print(f'Количество валидных адресов: {valid}')
print(f'Количество невалидных адресов: {invalid}')
print(f'Всего изменено адресов: {processed}')