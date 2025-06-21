import os
import tempfile
import shutil
import pytest
from unittest import mock

from etl.config import load_config

@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    for var in ["INPUT_PATH", "OUTPUT_PATH", "ANY_VAR"]:
        monkeypatch.delenv(var, raising=False)

def test_all_vars_and_paths_ok(monkeypatch, caplog):
    with tempfile.NamedTemporaryFile(delete=False) as infile:
        input_path = infile.name
    output_dir = tempfile.mkdtemp()
    output_path = os.path.join(output_dir, "out.txt")
    monkeypatch.setenv("INPUT_PATH", input_path)
    monkeypatch.setenv("OUTPUT_PATH", output_path)
    monkeypatch.setenv("ANY_VAR", "foo")
    required_vars = ["ANY_VAR"]
    path_vars = ["INPUT_PATH", "OUTPUT_PATH"]

    with caplog.at_level("INFO"):
        config = load_config(required_vars, path_vars)
    assert config["INPUT_PATH"] == input_path
    assert config["OUTPUT_PATH"] == output_path
    assert config["ANY_VAR"] == "foo"
    assert "Конфигурация успешно загружена" in caplog.text

    os.unlink(input_path)
    shutil.rmtree(output_dir)

def test_missing_required_var(monkeypatch):
    monkeypatch.setenv("INPUT_PATH", "/does/not/matter")
    monkeypatch.setenv("OUTPUT_PATH", "/does/not/matter")
    required_vars = ["ANY_VAR"]
    path_vars = ["INPUT_PATH", "OUTPUT_PATH"]
    with pytest.raises(EnvironmentError) as exc:
        load_config(required_vars, path_vars)
    assert "Отсутствуют обязательные переменные окружения: ANY_VAR" in str(exc.value)

def test_missing_path_var(monkeypatch):
    monkeypatch.setenv("ANY_VAR", "foo")
    monkeypatch.setenv("OUTPUT_PATH", "/some/path")
    required_vars = ["ANY_VAR"]
    path_vars = ["INPUT_PATH", "OUTPUT_PATH"]
    with pytest.raises(EnvironmentError) as exc:
        load_config(required_vars, path_vars)
    assert "Отсутствуют обязательные переменные окружения: INPUT_PATH" in str(exc.value)

def test_input_path_not_exists(monkeypatch):
    monkeypatch.setenv("ANY_VAR", "foo")
    monkeypatch.setenv("INPUT_PATH", "/no/such/file")
    monkeypatch.setenv("OUTPUT_PATH", "/tmp/out.txt")
    required_vars = ["ANY_VAR"]
    path_vars = ["INPUT_PATH", "OUTPUT_PATH"]
    with pytest.raises(FileNotFoundError) as exc:
        load_config(required_vars, path_vars)
    assert "Входной файл не существует: /no/such/file" in str(exc.value)

def test_output_dir_not_exists(monkeypatch):
    with tempfile.NamedTemporaryFile(delete=False) as infile:
        input_path = infile.name
    monkeypatch.setenv("ANY_VAR", "foo")
    monkeypatch.setenv("INPUT_PATH", input_path)
    monkeypatch.setenv("OUTPUT_PATH", "/no/such/dir/out.txt")
    required_vars = ["ANY_VAR"]
    path_vars = ["INPUT_PATH", "OUTPUT_PATH"]
    with pytest.raises(FileNotFoundError) as exc:
        load_config(required_vars, path_vars)
    assert "Выходная директория не существует: /no/such/dir" in str(exc.value)
    os.unlink(input_path)

def test_output_dir_empty(monkeypatch):
    with tempfile.NamedTemporaryFile(delete=False) as infile:
        input_path = infile.name
    monkeypatch.setenv("ANY_VAR", "foo")
    monkeypatch.setenv("INPUT_PATH", input_path)
    monkeypatch.setenv("OUTPUT_PATH", "out.txt")
    required_vars = ["ANY_VAR"]
    path_vars = ["INPUT_PATH", "OUTPUT_PATH"]
    config = load_config(required_vars, path_vars)
    assert config["OUTPUT_PATH"] == "out.txt"
    os.unlink(input_path)

@mock.patch("your_module.load_dotenv")
def test_load_dotenv_called(mock_load_dotenv, monkeypatch):
    with tempfile.NamedTemporaryFile(delete=False) as infile:
        input_path = infile.name
    output_dir = tempfile.mkdtemp()
    output_path = os.path.join(output_dir, "out.txt")
    monkeypatch.setenv("ANY_VAR", "foo")
    monkeypatch.setenv("INPUT_PATH", input_path)
    monkeypatch.setenv("OUTPUT_PATH", output_path)
    required_vars = ["ANY_VAR"]
    path_vars = ["INPUT_PATH", "OUTPUT_PATH"]
    load_config(required_vars, path_vars)
    mock_load_dotenv.assert_called_once()
    os.unlink(input_path)
    shutil.rmtree(output_dir)