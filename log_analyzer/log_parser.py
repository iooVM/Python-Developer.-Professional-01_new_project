import gzip
import re
from datetime import datetime
from typing import Iterator, Optional, Dict, Any, List


class NginxLogParser:
    LOG_FORMAT = re.compile(
        r'(?P<remote_addr>\S+)\s+'
        r'(?P<remote_user>\S+)\s+'
        r'(?P<http_x_forwarded_for>\S+)\s+'
        r'\[(?P<time_local>.+?)\]\s+'
        r'"(?P<request>.+?)"\s+'
        r'(?P<status>\d+)\s+'
        r'(?P<body_bytes_sent>\d+)\s+'
        r'"(?P<http_referer>.+?)"\s+'
        r'"(?P<http_user_agent>.+?)"\s+'
        r'"(?P<http_x_request_id>.+?)"\s+'
        r'"(?P<request_id>.+?)"\s+'
        r'(?P<request_time>\d+\.\d+)'
    )

    @classmethod
    def parse_line(cls, line: str) -> Optional[Dict[str, Any]]:
        try:
            match = cls.LOG_FORMAT.match(line.strip())
            if not match:
                return None

            data = match.groupdict()
            # Исправляем разбор полей http_x_request_id и request_id
            http_x_request_id = data['http_x_request_id'].strip('"')
            request_id = data['request_id'].strip('"')

            return {
                'remote_addr': data['remote_addr'],
                'remote_user': data['remote_user'],
                'http_x_forwarded_for': data['http_x_forwarded_for'],
                'time_local': datetime.strptime(
                    data['time_local'],
                    '%d/%b/%Y:%H:%M:%S %z'
                ),
                'request': data['request'],
                'status': int(data['status']),
                'body_bytes_sent': int(data['body_bytes_sent']),
                'http_referer': data['http_referer'],
                'http_user_agent': data['http_user_agent'],
                'http_x_request_id': http_x_request_id,
                'request_id': request_id,
                'request_time': float(data['request_time']),
            }
        except (ValueError, AttributeError) as e:
            return None

    @classmethod
    def parse_file(cls, file_path: str) -> Iterator[Optional[Dict[str, Any]]]:
        """Парсит файл логов построчно"""
        open_func = gzip.open if file_path.endswith('.gz') else open
        mode = 'rt' if file_path.endswith('.gz') else 'r'

        try:
            with open_func(file_path, mode, encoding='utf-8') as f:
                for line in f:
                    parsed = cls.parse_line(line)
                    if parsed is not None:  # Фильтруем None значения
                        yield parsed
        except (IOError, UnicodeDecodeError) as e:
            raise ValueError(f"Failed to read log file: {str(e)}")


def parse_log_line(line: str) -> Optional[Dict[str, Any]]:
    return NginxLogParser.parse_line(line)


def parse_nginx_logs(log_file: str, error_threshold: float = 0.5) -> Dict[str, Any]:
    total = 0
    failed = 0
    parsed_data = []
    total_time = 0.0

    for record in NginxLogParser.parse_file(log_file):
        if record is None:
            failed += 1
        else:
            parsed_data.append(record)
        total += 1

    error_rate = round(failed / total, 3) if total > 0 else 0

    if error_rate > error_threshold:
        raise ValueError(
            f"Error rate {error_rate:.3f} exceeds threshold {error_threshold:.3f}"
        )

    return {
        'total': total,
        'parsed': total - failed,
        'failed': failed,
        'error_rate': error_rate,
        'total_time': round(total_time, 3),
        'data': parsed_data,
    }


def calculate_stats(parsed_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    url_stats = {}
    total_time = 0.0
    total_requests = 0

    for log in parsed_logs:
        request = log["request"]
        request_time = log["request_time"]
        url = request.split()[1] if " " in request else request

        if url not in url_stats:
            url_stats[url] = {
                "count": 0,
                "time_sum": 0.0,
                "times": [],
            }

        url_stats[url]["count"] += 1
        url_stats[url]["time_sum"] += request_time
        url_stats[url]["times"].append(request_time)
        total_time += request_time
        total_requests += 1

    stats = []
    for url, data in url_stats.items():
        times = sorted(data["times"])
        stats.append({
            "url": url,
            "count": data["count"],
            "count_perc": round((data["count"] / total_requests) * 100, 3),
            "time_sum": round(data["time_sum"], 3),
            "time_perc": round((data["time_sum"] / total_time) * 100, 3) if total_time > 0 else 0,
            "time_avg": round(data["time_sum"] / data["count"], 3),
            "time_max": round(max(times), 3),
            "time_med": round(times[len(times) // 2], 3),
        })

    return stats

__all__ = [
    'NginxLogParser',
    'parse_nginx_logs',
    'calculate_stats',
    'parse_log_line'
]