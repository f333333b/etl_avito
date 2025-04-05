# скрипт для вставки в таблицу ссылок на короткие видео из другой таблицы по ID объявления

import pandas as pd
from openpyxl import load_workbook


old_file = pd.read_excel(r'C:\Users\user\Desktop\short_videos.xlsx')
new_file = pd.read_excel(r'C:\Users\user\Desktop\table28.03.2025source.xlsx')
if 'VideoFileURL' in new_file.columns:
    del new_file['VideoFileURL']
merged_file = new_file.merge(old_file[['AvitoId', 'VideoFileURL']], on='AvitoId', how='left')
merged_file.to_excel(r'C:\Users\user\Desktop\file_updated.xlsx', index=False)
added_links_count = merged_file['VideoFileURL'].notna().sum()
print(f"Добавлено ссылок на видео: {added_links_count}")

# прикрепление первой строки в таблице
wb = load_workbook(r'C:\Users\user\Desktop\file_updated.xlsx')
ws = wb.active
ws.freeze_panes = "A2"
wb.save(r'C:\Users\user\Desktop\file_updated.xlsx')