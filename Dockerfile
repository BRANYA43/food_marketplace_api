FROM python:3.11-slim

RUN apt-get update; \
    apt-get install -y --no-install-recommends build-essential libpq-dev gcc mc nano curl; \
    rm -rf /var/lib/apt/lists/*; \
    python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 DOCKER_RUN=1

WORKDIR /opt/src/

COPY requirements.txt .

RUN pip install --upgrade pip; \
    pip install -r requirements.txt --no-cache-dir; \
    rm requirements.txt

COPY /src .