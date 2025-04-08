import gzip
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from log_analyzer.log_parser import (
    NginxLogParser,
    parse_nginx_logs,
    calculate_stats,
    parse_log_line
)


@pytest.fixture
def sample_log_line():
    return (
        '1.196.116.32 - - [29/Jun/2017:03:50:22 +0300] '
        '"GET /api/v2/banner/25019354 HTTP/1.1" 200 927 "-" '
        '"Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5" "-" '
        '"1498697422-2190034393-4708-9752759" "dc7161be3" 0.390'
    )


@pytest.fixture
def sample_parsed_data():
    return {
        'remote_addr': '1.196.116.32',
        'remote_user': '-',
        'http_x_forwarded_for': '-',
        'time_local': datetime.strptime('29/Jun/2017:03:50:22 +0300', '%d/%b/%Y:%H:%M:%S %z'),
        'request': 'GET /api/v2/banner/25019354 HTTP/1.1',
        'status': 200,
        'body_bytes_sent': 927,
        'http_referer': '-',
        'http_user_agent': 'Lynx/2.8.8dev.9 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/2.10.5',
        'http_x_request_id': '1498697422-2190034393-4708-9752759',
        'request_id': 'dc7161be3',
        'request_time': 0.390
    }



class TestNginxLogParser:

    def test_parse_file_io_error(self):
        with patch('builtins.open', side_effect=IOError("File error")):
            with pytest.raises(ValueError, match="Failed to read log file"):
                list(NginxLogParser.parse_file('/path/to/nonexistent.log'))


class TestParseNginxLogs:
    @patch('log_analyzer.log_parser.NginxLogParser.parse_file')
    def test_successful_parse(self, mock_parse, sample_parsed_data):
        mock_parse.return_value = [sample_parsed_data, sample_parsed_data]

        with tempfile.NamedTemporaryFile() as tmp:
            result = parse_nginx_logs(tmp.name, error_threshold=0.5)

            assert result['total'] == 2
            assert result['parsed'] == 2
            assert result['failed'] == 0
            assert result['error_rate'] == 0.0

    @patch('log_analyzer.log_parser.NginxLogParser.parse_file')
    def test_high_error_rate(self, mock_parse):
        mock_parse.return_value = [None, None, {"request": "GET /test HTTP/1.1", "request_time": 0.1}]

        with tempfile.NamedTemporaryFile() as tmp:
            with pytest.raises(ValueError, match="Error rate 0.667 exceeds threshold 0.500"):
                parse_nginx_logs(tmp.name, error_threshold=0.5)

