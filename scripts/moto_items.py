# Мини-скрипт для проверки наличия ключевых слов (брендов) из списка motorcycles в файле объявлений

import os
import pandas as pd
import argparse

# обработка аргументов
parser = argparse.ArgumentParser()
parser.add_argument('--input', required=True)
args = parser.parse_args()

# формирование пути к файлу
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
input_path = os.path.join(desktop_path, args.input)

# загрузка таблицы
df = pd.read_excel(input_path)

# счётчик найденных совпадений
counter = 0

# чтение файла с моделями мототехники
with open('moto_items.txt', 'r', encoding='utf-8') as f:
    brands = [line.strip() for line in f if line.strip()]

# проверка по каждой строке
for brand in brands:
    title_match = df['Title'].astype(str).str.contains(brand, regex=False, na=False)
    desc_match = df['Description'].astype(str).str.contains(brand, regex=False, na=False)

    if title_match.any() or desc_match.any():
        print(f'Техника "{brand}" найдена.')
        counter += 1

print(f'Всего найдено брендов: {counter}')