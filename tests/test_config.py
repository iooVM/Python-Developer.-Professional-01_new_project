import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from log_analyzer.config import Config, get_config


def test_default_config():
    """Тестирование конфига по умолчанию"""
    config = Config()
    assert config.REPORT_SIZE == 1000
    assert config.REPORT_DIR == "./reports"
    assert config.LOG_DIR == "./log"
    assert config.LOG_FILE is None


def test_config_from_dict():
    """Тестирование создания конфига из словаря"""
    config_dict = {
        "REPORT_SIZE": 500,
        "REPORT_DIR": "/custom/reports",
        "LOG_DIR": "/custom/logs",
        "LOG_FILE": "/var/log/log_analyzer.log",
        "EXTRA_PARAM": "value"  # Должен быть проигнорирован
    }
    config = Config.from_dict(config_dict)
    
    assert config.REPORT_SIZE == 500
    assert config.REPORT_DIR == "/custom/reports"
    assert config.LOG_DIR == "/custom/logs"
    assert config.LOG_FILE == "/var/log/log_analyzer.log"
    assert not hasattr(config, "EXTRA_PARAM")


def test_load_config(tmp_path):
    """Тестирование загрузки конфига из файла"""
    config_file = tmp_path / "config.json"
    config_data = {
        "REPORT_SIZE": 200,
        "LOG_DIR": "/test/logs"
    }
    config_file.write_text(json.dumps(config_data))
    
    config = Config.load_config(str(config_file))
    
    assert config.REPORT_SIZE == 200
    assert config.LOG_DIR == "/test/logs"
    # Остальные параметры должны быть из дефолтного конфига
    assert config.REPORT_DIR == "./reports"
    assert config.LOG_FILE is None


def test_load_config_file_not_found():
    """Тестирование обработки отсутствия файла конфига"""
    with pytest.raises(FileNotFoundError):
        Config.load_config("/nonexistent/path/config.json")


def test_load_config_invalid_json(tmp_path):
    """Тестирование обработки невалидного JSON"""
    config_file = tmp_path / "bad_config.json"
    config_file.write_text("{invalid json}")
    
    with pytest.raises(ValueError):
        Config.load_config(str(config_file))


def test_get_config_default():
    """Тестирование get_config без указания файла"""
    config = get_config()
    assert config.REPORT_SIZE == 1000
    assert config.REPORT_DIR == "./reports"


def test_get_config_with_file(tmp_path):
    """Тестирование get_config с указанием файла"""
    config_file = tmp_path / "test_config.json"
    config_file.write_text(json.dumps({"REPORT_SIZE": 300}))
    
    config = get_config(str(config_file))
    assert config.REPORT_SIZE == 300
    assert config.REPORT_DIR == "./reports"  # Из дефолтного конфига


@patch("log_analyzer.config.Config.load_config")
def test_get_config_with_none(mock_load):
    """Тестирование get_config с None вместо пути"""
    config = get_config(None)
    mock_load.assert_not_called()
    assert isinstance(config, Config)
    assert config.REPORT_SIZE == 1000


def test_config_immutability():
    """Тестирование, что конфиг нельзя изменить после создания"""
    config = Config()
    
    with pytest.raises(AttributeError):
        config.REPORT_SIZE = 2000
    
    with pytest.raises(AttributeError):
        config.NEW_PARAM = "value"