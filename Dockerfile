FROM python:3.8-slim

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --no-interaction --no-ansi

COPY . .

ENV LOG_DIR=/log
ENV REPORT_DIR=/reports

CMD ["python", "-m", "log_analyzer"]