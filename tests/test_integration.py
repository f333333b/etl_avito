import shutil
import pandas as pd
from pathlib import Path
from main import run_etl
from dotenv import set_key, load_dotenv
import logging

def test_pipeline_integration(tmp_path, caplog):
    dotenv_path = Path(".env")
    load_dotenv(dotenv_path)
    input_sample = Path("data/input_sample.xlsx")
    temp_input = tmp_path / "input_sample.xlsx"
    shutil.copy(input_sample, temp_input)
    temp_output = tmp_path / "output_sample.xlsx"
    set_key(dotenv_path, "INPUT_PATH", str(temp_input))
    set_key(dotenv_path, "OUTPUT_PATH", str(temp_output))
    load_dotenv(dotenv_path, override=True)
    Path("validation_logs").mkdir(parents=True, exist_ok=True)
    caplog.set_level(logging.INFO)
    run_etl()
    assert temp_output.exists(), "Файл не был создан"
    df = pd.read_excel(temp_output)
    assert not df.empty, "Результирующий файл пуст"
    assert "ERROR" not in caplog.text
    assert "ошибка" not in caplog.text.lower()
    set_key(dotenv_path, "INPUT_PATH", "C:/Users/user/Desktop/sample.xlsx")
    set_key(dotenv_path, "OUTPUT_PATH", "C:/Users/user/Desktop/output.xlsx")
