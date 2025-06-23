import os
import logging
import pandas as pd

logger = logging.getLogger(__name__)

def read_excel_file(path: str) -> pd.DataFrame:
    """Функция чтения Excel-файла"""
    if not os.path.isfile(path):
        logger.error(f"Файл не найден: {path}")
        raise FileNotFoundError(f"Файл не найден: {path}")
    try:
        df = pd.read_excel(path)
        logger.info(f"Файл успешно прочитан: {path}, строк: {len(df)}")
        required_columns = ['Id', 'Address', 'Category', 'Title', 'Description', 'VehicleType', 'Make', 'Model', 'Type',
                            'Year', 'Availability', 'Condition']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            error_msg = f"Отсутствуют обязательные колонки: {', '.join(missing_columns)}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        return df
    except Exception as e:
        logger.exception(f"Ошибка при чтении файла {path}: {e}")
        raise