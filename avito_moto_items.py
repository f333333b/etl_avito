import pandas as pd
from avito_moto_items_data import motorcycles

table = pd.read_excel(r'table.xlsx')
for item in motorcycles:
    if table['Title'].str.contains(item[15], regex=False).any() or table['Description'].str.contains(item[15], regex=False).any():
        print(f'Техника {item} найдена.')