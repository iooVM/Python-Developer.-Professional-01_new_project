import json
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Optional, Dict, Any

import structlog

logger = structlog.get_logger()


@dataclass(frozen=True)  # Делаем класс неизменяемым
class Config:
    REPORT_SIZE: int = 1000
    REPORT_DIR: str = "./reports"
    LOG_DIR: str = "./log"
    LOG_FILE: Optional[str] = None

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "Config":
        return cls(**{
            k: v for k, v in config_dict.items()
            if k in {f.name for f in fields(cls)}
        })

    @classmethod
    def load_config(cls, config_path: str = "config.json") -> "Config":
        default_config = cls()

        try:
            config_path_obj = Path(config_path)
            if not config_path_obj.exists():
                logger.error("Config file not found", path=config_path)
                raise FileNotFoundError(f"Config file not found: {config_path}")

            with open(config_path, "r") as f:
                file_config = json.load(f)

            return cls.from_dict({**default_config.__dict__, **file_config})

        except json.JSONDecodeError as e:
            logger.error("Failed to parse config file", error=str(e))
            raise ValueError(f"Invalid config file: {e}")


def get_config(config_path: Optional[str] = None) -> Config:
    return Config.load_config(config_path) if config_path else Config()