'''
Скрипт для вставки в Excel-таблицу ссылок на короткие видео из другой Excel-таблицы по ID объявления.
По умолчанию для удобства ожидает, что файлы находятся на рабочем столе.
'''

import pandas as pd
import argparse
from datetime import datetime
import os
from freeze_1st_row import freeze_1st_row

# обработка аргументов
parser = argparse.ArgumentParser(description="Добавление коротких видео по ID объявления")
parser.add_argument('--input', required=True)
parser.add_argument('--videos', required=True)
args = parser.parse_args()

# обработка путей к файлам
desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
input_path = os.path.join(desktop_path, args.input)
videos_path = os.path.join(desktop_path, args.videos)

# загрузка таблиц
df_main = pd.read_excel(input_path)
df_videos = pd.read_excel(videos_path)

print('Обработка таблиц в процессе.')

# удаляем колонку VideoFileURL, если уже есть
if 'VideoFileURL' in df_main.columns:
    del df_main['VideoFileURL']

# объединение по AvitoId
merged_df = df_main.merge(df_videos[['AvitoId', 'VideoFileURL']], on='AvitoId', how='left')

# сохранение
timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
output_file = os.path.join(desktop_path, f"file_updated_{timestamp}.xlsx")
merged_df.to_excel(output_file, index=False)

# заморозка первой строки
freeze_1st_row(output_file)

# подсчёт добавленных ссылок
added_links_count = merged_df['VideoFileURL'].notna().sum()
print(f"Обработка завершена. Добавлено ссылок на видео: {added_links_count}.")
print(f"Файл сохранён: {output_file}")
