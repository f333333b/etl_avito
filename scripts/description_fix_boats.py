"""
Скрипт для редактирования Excel-файла с объявлениями:
- фильтрует строки по типу транспорта
- разделяет описание по ключевому разделителю
- добавляет блок с ключевыми словами
- сохраняет обновлённый Excel-файл
"""

import pandas as pd
import argparse
import os

SEPARATOR = '-' * 40 + '<br>'
SPLIT_MARKER = '<p>лодочные моторы'

KEYWORDS_BOATS = '''ЛОДКИ: MISHIMO/МИШИМО, SMARINE-X-MOTORS-EDITION/СМАРИН ЭДИШЕН, OMOLON/ОМОЛОН, GLADIATOR/ГЛАДИАТОР, ДРАККАР, SMARINE/СМАРИН,
GLADIATOR/ГЛАДИАТОР, SEA-PRO/СИА ПРО, GLADIATOR-X-MOTORS-EDITION/ГЛАДИАТОР ЭДИШЕН, ROGER/РОГЕР, АДМИРАЛ, SOLAR/СОЛАР, SIBRIVER/СИБРИВЕР, РАКЕТА, 
РИВЬЕРА, ТАЙМЕНЬ, ФРЕГАТ, X-RIVER/ ИКСРИВЕР, REEF/РИФ, APACHE/АПАЧИ, PELICAN/ПЕЛИКАН'''

KEYWORDS_ENGINES = '''ЛОДОЧНЫЕ МОТОРЫ: MARLIN/МАРЛИН, PROMAX/ПРОМАКС, MARLIN PROLINE/МАРЛИН ПРОЛАЙН, BREEZE-YAMAHA/БРИЗ
ЯМАХА, CONDOR/КОНДОР, STELS/СТЕЛС, TAKATSU/ТАХАЦУ, GLADIATOR/ГЛАДИАТОР, YAMAHA/ЯМАХА, MERCURY/МЕРКУРИ, HONDA/ХОНДА, HANGKAI/ХАНГАЙ, HDX, HIDEA/ХИДЕА, 
SEA-PRO/СИАПРО, PARSUN/ПАРСУН, TOHATSU/ТОХАЦУ'''

def update_description_by_type(df, split_marker):
    vehicle_type_filter = df['VehicleType'] == 'Моторные лодки и моторы'
    filtered = df[vehicle_type_filter]
    rows = list(zip(filtered['AvitoId'], filtered['Description'], filtered['Type']))
    print(f'Всего объявлений для обработки: {len(rows)}')
    
    for avito_id, description, item_type in rows:
        if pd.isna(avito_id) or pd.isna(description):
            continue

        description_parts = str(description).split(split_marker)
        if item_type == 'Лодочный мотор':
            new_block = KEYWORDS_ENGINES
        else:
            new_block = KEYWORDS_BOATS

        new_description = ''.join(description_parts + [SEPARATOR, new_block])
        df.loc[df['AvitoId'] == avito_id, 'Description'] = new_description

def main(input_path, output_path):
    if not os.path.exists(input_path):
        print(f'Файл не найден: {input_path}')
        return

    df = pd.read_excel(input_path)
    update_description_by_type(df, SPLIT_MARKER)
    df.to_excel(output_path, index=False)
    print(f'Обновлённый файл сохранён: {output_path}')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Excel description updater for Avito ads.")
    parser.add_argument("--input", required=True, help="Путь к входному Excel-файлу")
    parser.add_argument("--output", required=True, help="Путь к выходному Excel-файлу")
    args = parser.parse_args()

    main(args.input, args.output)
