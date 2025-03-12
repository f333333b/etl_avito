# скрипт для вставки в таблицу ссылок на короткие видео из другой таблицы по ID объявления

import pandas as pd

old_file = pd.read_excel('file_with_short_videos.xlsx')
new_file = pd.read_excel('file_new.xlsx')
merged_file = new_file.merge(old_file[['AvitoId', 'VideoFileURL']], on='AvitoId', how='left')
merged_file.to_excel('file_updated.xlsx', index=False)
added_links_count = merged_file['VideoFileURL'].notna().sum()
print(f"Добавлено ссылок на видео: {added_links_count}")