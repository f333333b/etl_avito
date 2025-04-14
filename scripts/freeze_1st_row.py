'''Замораживает первую строку Excel-файла (панель с заголовками)'''
from openpyxl import load_workbook
import os

def freeze_1st_row(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    wb = load_workbook(file_path)
    wb.active.freeze_panes = "A2"
    wb.save(file_path)