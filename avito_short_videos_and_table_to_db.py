import pandas as pd
from openpyxl import load_workbook
from sqlalchemy import create_engine
from datetime  import datetime

def main():
    engine = create_engine('postgresql://postgres:1@localhost:5432/postgres')
    add_short_videos()
    xls_to_sql(engine)
    sql_to_xls(engine)

def add_short_videos():
    '''Функция вставки ссылок с короткими видео
    Ссылки из таблицы 'short_videos.xlsx' вставляются в текущую таблицу
    на основании соотношения значения столбца 'AvitoID'
    '''
    old_file = pd.read_excel('short_videos.xlsx')
    new_file = pd.read_excel(r'C:\Users\fgkh\Desktop\table.xlsx')
    if 'VideoFileURL' in new_file.columns:
        del new_file['VideoFileURL']
    merged_file = new_file.merge(old_file[['AvitoId', 'VideoFileURL']], on='AvitoId', how='left')
    merged_file.to_excel(r'C:\Users\fgkh\Desktop\file_updated.xlsx', index=False)
    added_links_count = merged_file['VideoFileURL'].notna().sum()
    print(f"Добавлено ссылок на видео: {added_links_count}")

    # прикрепление первой строки в таблице
    wb = load_workbook("file_updated.xlsx")
    ws = wb.active
    ws.freeze_panes = "A2"
    wb.save("file_updated.xlsx")


def xls_to_sql(engine):
    '''Функция создания таблицы (замены существующей) в базе данных PostgreSQL на основании Excel таблицы'''
    df = pd.read_excel(r'C:\Users\fgkh\Desktop\file_updated.xlsx')
    print(f"Всего строк в таблице: {len(df)}")
    df.to_sql(f'xm', engine, if_exists='replace', index=False)
    print("Данные успешно загружены в таблицу 'xm' PostgreSQL")

def sql_to_xls(engine):
    '''Функция создания Excel таблицы на основании таблицы в базе данных PostgreSQL'''
    df = pd.read_sql_table('xm', engine)
    current_datetime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = rf'C:\Users\fgkh\Desktop\xm_{current_datetime}.xlsx'
    df.to_excel(output_file, index=False, engine='openpyxl')
    print(f'Таблица сохранена в файл {output_file}')

if __name__ == "__main__":
    main()