# скрипт для добавления недостающих объявлений в файл (по номеру ID)

import pandas as pd
from openpyxl import load_workbook

counter = 0
full_file = pd.read_excel(r'C:\Users\user\Desktop\table.xlsx')
new_file = pd.read_excel(r'C:\Users\user\Desktop\new_file.xlsx')

for index, row in full_file.iterrows():
    #print(index, row)
    if row['Id'] not in new_file['Id'].values:
        counter += 1
        new_file = new_file._append(row, ignore_index=True)

new_file.to_excel(r'C:\Users\user\Desktop\file_updated.xlsx', index=False)

# прикрепление первой строки в таблице
wb = load_workbook(r'C:\Users\user\Desktop\file_updated.xlsx')
ws = wb.active
ws.freeze_panes = "A2"
wb.save(r'C:\Users\user\Desktop\file_updated.xlsx')
print(counter)