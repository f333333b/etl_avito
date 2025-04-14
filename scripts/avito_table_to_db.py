import pandas as pd
from sqlalchemy import create_engine
from datetime  import datetime

df = pd.read_excel(r'C:\Users\fgkh\Desktop\file_updated.xlsx')
print(df.head())
print(f"Всего строк: {len(df)}")

engine = create_engine('postgresql://postgres:1@localhost:5432/postgres')
current_date_and_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
print(current_date_and_time)
df.to_sql(f'xm_{current_date_and_time}', engine, if_exists='replace', index=False)
print("Данные загружены в PostgreSQL")