import json
from datetime import datetime
from pathlib import Path
from string import Template
from typing import List, Dict, Any

import structlog

logger = structlog.get_logger()


def render_report_template(stats: List[Dict[str, Any]], report_date: datetime, report_size: int) -> str:
    with open("report.html", "r", encoding="utf-8") as f:
        template = Template(f.read())

    sorted_stats = sorted(stats, key=lambda x: x["time_sum"], reverse=True)[:report_size]

    return template.safe_substitute({
        "table_json": json.dumps(sorted_stats, ensure_ascii=False)
    })


def save_report(report_content: str, report_dir: str, report_date: datetime) -> bool:
    report_dir_path = Path(report_dir)
    if not report_dir_path.exists():
        report_dir_path.mkdir(parents=True)
        logger.info("Created report directory", path=report_dir)

    report_filename = f"report-{report_date.strftime('%Y.%m.%d')}.html"
    report_path = report_dir_path / report_filename

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report_content)
        logger.info("Report saved successfully", path=str(report_path))
        return True
    except IOError as e:
        logger.error("Failed to save report", path=str(report_path), error=str(e))
        return False


def generate_report(stats: List[Dict[str, Any]], config: "Config", report_date: datetime) -> bool:
    if not stats:
        logger.error("No stats to generate report")
        return False

    report_content = render_report_template(stats, report_date, config.REPORT_SIZE)
    return save_report(report_content, config.REPORT_DIR, report_date)