import argparse
import sys
import logging
import structlog
from pathlib import Path
from typing import Optional

from .config import Config, get_config
from .utils import find_latest_log
from .log_parser import parse_nginx_logs, calculate_stats
from .report_generator import generate_report


def setup_logging(log_file: Optional[str] = None):
    """Настройка логирования"""
    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
    )

    handler = logging.FileHandler(log_file) if log_file else logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logging.basicConfig(handlers=[handler], level=logging.INFO)


def main():
    """Точка входа"""
    setup_logging()
    logger = structlog.get_logger()

    try:
        parser = argparse.ArgumentParser(description="Log analyzer for nginx logs")
        parser.add_argument("--config", help="Path to config file", default="config.json")
        args = parser.parse_args()

        try:
            config = get_config(args.config)
        except FileNotFoundError:
            logger.warning("Config file not found, using defaults", path=args.config)
            config = Config()

        if config.LOG_FILE:
            setup_logging(config.LOG_FILE)

        logger.info("Starting log analyzer", config=config.__dict__)

        log_info = find_latest_log(config.LOG_DIR)
        if not log_info:
            logger.error("No log files found")
            return 1

        logger.info("Found log file", path=str(log_info.path), date=str(log_info.date))

        report_filename = f"report-{log_info.date.strftime('%Y.%m.%d')}.html"
        report_path = Path(config.REPORT_DIR) / report_filename
        if report_path.exists():
            logger.info("Report already exists", path=str(report_path))
            return 0

        result = parse_nginx_logs(str(log_info.path))
        if not result:
            return 1

        stats = calculate_stats(result['data'])
        logger.info(
            "Log stats calculated",
            total_requests=result['total'],
            total_time=result['total_time'],
            unique_urls=len(stats),
        )

        if not generate_report(stats, config, log_info.date):
            return 1

        return 0

    except Exception as e:
        logger.error("Unexpected error", error=str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())