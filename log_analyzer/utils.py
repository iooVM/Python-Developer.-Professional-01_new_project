import gzip
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, TextIO

import structlog

logger = structlog.get_logger()


@dataclass
class LogFileInfo:
    path: Path
    date: datetime
    extension: str


def find_latest_log(log_dir: str) -> Optional[LogFileInfo]:
    log_dir_path = Path(log_dir)
    if not log_dir_path.exists():
        return None

    latest_log = None
    pattern = re.compile(r"nginx-access-ui\.log-(?P<date>\d{8})(\.(?P<ext>gz))?$")

    for file in log_dir_path.iterdir():
        if not file.is_file():
            continue

        match = pattern.fullmatch(file.name)
        if not match:
            continue

        date_str = match.group("date")
        try:
            date = datetime.strptime(date_str, "%Y%m%d")
        except ValueError:
            continue

        extension = match.group("ext") or ""

        if latest_log is None or date > latest_log.date:
            latest_log = LogFileInfo(path=file, date=date, extension=extension)

    return latest_log


def open_log_file(log_info: LogFileInfo) -> Union[TextIO, gzip.GzipFile]:
    if log_info.extension == "gz":
        return gzip.open(log_info.path, "rt", encoding="utf-8")
    return open(log_info.path, "r", encoding="utf-8")

__all__ = [
    'LogFileInfo',
    'find_latest_log',
    'open_log_file'
]