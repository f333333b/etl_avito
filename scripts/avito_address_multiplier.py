"""
Скрипт для клонирования строк в Excel-файле:
- берёт список ID
- для каждого ID создаёт копии с разными адресами (из переменной окружения ADDRESSES (файл .env)
- обновлённые строки добавляются в исходный DataFrame
- также проставляется Id всех добавленных строк
- результат сохраняется в новый Excel-файл
"""

import pandas as pd
import argparse
from datetime import datetime
import os
from freeze_1st_row import freeze_1st_row
from dotenv import load_dotenv

# парсинг аргументов
parser = argparse.ArgumentParser(description="Клонирование строк с определенным ID по разным адресам")
parser.add_argument('--input', required=True)
parser.add_argument('--ids', required=True)
args = parser.parse_args()

# обработка путей к файлам и переменные
load_dotenv()
addresses = os.getenv('ADDRESSES').split(';')
addresses = [a.strip() for a in addresses if a.strip()]
added_rows_count = 0
id_counter = 1
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
file_path = os.path.join(desktop_path, args.input)
ids_file = os.path.join(desktop_path, args.ids)
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file = os.path.join(desktop_path, f"file_updated_{timestamp}.xlsx")

print('Обработка таблицы в процессе.')

# обработка файлов
with open(ids_file, 'r', encoding='utf-8') as f:
    ids = f.read().strip().split(',')
    ids = [i.strip() for i in ids if i.strip()]

df = pd.read_excel(file_path)
result_df = df
rows_to_add = []
for id in ids:
    row = df[df['AvitoId'] == int(id)]
    if not row.empty:
        for address in addresses:
            new_row = row.copy()
            new_row['AvitoId'] = None
            new_row['AvitoDateEnd'] = None
            new_row['Address'] = address
            new_row['Id'] = f"08042025sg{id_counter:05d}"
            new_row = new_row.dropna(axis=1, how='all')
            rows_to_add.append(new_row)
            added_rows_count += 1
            id_counter += 1

if rows_to_add:
    additions_df = pd.concat(rows_to_add, ignore_index=True)
    result_df = pd.concat([df, additions_df], ignore_index=True)

result_df.to_excel(output_file, index=False)
freeze_1st_row(output_file)
print(f"Количество добавленных строк: {added_rows_count}")
print("Файл сохранён:", output_file)
