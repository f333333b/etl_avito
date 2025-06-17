import pandas as pd

def read_excel_file(path: str) -> pd.DataFrame:
    return pd.read_excel(path)