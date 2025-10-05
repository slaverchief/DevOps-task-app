FROM ubuntu:22.04

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

WORKDIR /app


COPY requirements.txt .

RUN apt update && apt install python3 -y && apt install python3-pip -y && \
    pip3 install --upgrade pip && \
    pip3 install -r requirements.txt

COPY . .



