import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

# список ID, которые нужно размножить
ids = []

file_path = r'C:\Users\user\Desktop\file_updated.xlsx'
df = pd.read_excel(file_path)
addresses = os.getenv('ADDRESSES')
added_rows_count = 0
id_counter = 1

for id in ids:
    row = df[df['AvitoId'] == int(id)]
    if not row.empty:
        for address in addresses:
            new_row = row.copy()
            new_row['AvitoId'] = None
            new_row['AvitoDateEnd'] = None
            new_row['Address'] = address
            new_row['Id'] = f"08042025sg{id_counter:05d}"
            df = pd.concat([df, new_row], ignore_index=True)
            added_rows_count += 1
            id_counter += 1

print(f"Количество добавленных строк: {added_rows_count}")
df.to_excel(r'C:\Users\user\Desktop\file_updated_23.xlsx', index=False)