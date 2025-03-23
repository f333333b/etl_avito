import pandas as pd
from sqlalchemy import create_engine

df = pd.read_excel('xm.xlsx')
print(df.head())
print(f"Всего строк: {len(df)}")

engine = create_engine('postgresql://postgres:1@localhost:5432/postgres')
df.to_sql('xm', engine, if_exists='replace', index=False)
print("Данные загружены в PostgreSQL")