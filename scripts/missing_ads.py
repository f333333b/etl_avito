# Скрипт для добавления недостающих объявлений в файл (по номеру ID)

import os
import pandas as pd
import argparse
from datetime import datetime
from freeze_1st_row import freeze_1st_row

if __name__ == "__main__":
    # обработка аргументов
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    args = parser.parse_args()
    desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
    input_path = os.path.join(desktop_path, args.input)

    # проверка пути к таблице
    if not os.path.exists(input_path):
        print(f"Файл не найден: {input_path}")
        exit(1)

    # обработка таблицы
    df_main = pd.read_excel(input_path)
    df_result = pd.DataFrame(columns=df_main.columns)
    existing_ids = set()
    counter = 0
    for index, row in df_main.iterrows():
        row_id = row['Id']
        if row_id not in existing_ids:
            df_result = pd.concat([df_result, pd.DataFrame([row])], ignore_index=True)
            existing_ids.add(row_id)
            counter += 1

    # сохранение нового файла таблицы
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"file_updated_{timestamp}.xlsx"
    output_path = os.path.join(desktop_path, output_filename)
    df_result.to_excel(output_path, index=False)

    # заморозка первой строки
    freeze_1st_row(output_path)

    print(f'Количество добавленных новых (уникальных) строк: {counter}')
    print(f'Файл сохранён: {output_path}')
