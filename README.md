# Log Analyzer

Анализатор логов nginx для выявления медленных URL.

## Установка

1. Установите Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
2. Установите зависимости:
```
poetry install
```
## Запуск анализатора
```
poetry run python -m log_analyzer [--config path/to/config.json]
```
## Тестирование
```
poetry run pytest
```
## Линтинг 
```
make lint
```
## Пример конфигурационного файла config.json: 
```
{
    "REPORT_SIZE": 1000,
    "REPORT_DIR": "./reports",
    "LOG_DIR": "./log",
    "LOG_FILE": "./log_analyzer.log"
}
```
## Для запуска в Docker:
```
docker build -t log-analyzer .
docker run -v /path/to/logs:/log -v /path/to/reports:/reports log-analyzer
```
