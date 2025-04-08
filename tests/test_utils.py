import re
from datetime import datetime
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from log_analyzer.utils import (
    LogFileInfo,
    find_latest_log,
    open_log_file
)


def test_find_latest_log(tmp_path):
    log_dir = tmp_path / "log"
    log_dir.mkdir()

    (log_dir / "nginx-access-ui.log-20250101").write_text("")
    (log_dir / "nginx-access-ui.log-20250102.gz").write_text("")
    (log_dir / "nginx-access-ui.log-20250103").write_text("")
    (log_dir / "other-file.txt").write_text("")

    result = find_latest_log(str(log_dir))
    assert result is not None
    assert result.path.name == "nginx-access-ui.log-20250103"
    assert result.date == datetime(2025, 1, 3)
    assert result.extension == ""


def test_find_latest_log_no_files(tmp_path):
    result = find_latest_log(str(tmp_path))
    assert result is None


def test_open_log_file_plain(tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text("test content")
    log_info = LogFileInfo(path=log_file, date=datetime.now(), extension="")

    with open_log_file(log_info) as f:
        assert f.read() == "test content"


@patch('gzip.open', new_callable=mock_open)
def test_open_log_file_gzip(mock_gzip):
    log_info = LogFileInfo(
        path=Path("/path/to/log.gz"),
        date=datetime.now(),
        extension="gz"
    )
    mock_gzip.return_value.__enter__.return_value.read.return_value = "gzipped content"

    with open_log_file(log_info) as f:
        assert f.read() == "gzipped content"