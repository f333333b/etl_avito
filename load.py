import os
import logging
import pandas as pd

def save_to_excel(df: pd.DataFrame, path: str) -> None:
    df = df.copy()

    # Проверка существования папки
    folder = os.path.dirname(path)
    if folder and not os.path.isdir(folder):
        logging.error(f"Папка не существует: {folder}")
        raise FileNotFoundError(f"Папка не существует: {folder}")

    # Удаление tz-информации из datetime с таймзоной
    for col in df.select_dtypes(include=["datetimetz"]).columns:
        df[col] = df[col].dt.tz_localize(None)

    df.to_excel(path, index=False)