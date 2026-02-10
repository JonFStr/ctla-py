# Base image, runs once and exits
FROM python:3-alpine AS oneshot
LABEL authors="Jonathan Straub"

WORKDIR /app
ENV PYTHONPATH=/usr/src/ctla
ENV OUTPUT_DIR=/onedrive
ENV REMOTE_NAME=sharepoint
ENV REMOTE_PATH=/songs

RUN apk add --no-cache rclone

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt  \
    && rm requirements.txt

COPY ./ctla /usr/src/ctla
COPY ./tools /usr/src/tools
