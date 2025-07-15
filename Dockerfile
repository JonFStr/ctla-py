# Base image, runs once and exits
FROM python:3-alpine AS oneshot
LABEL authors="Jonathan Straub"

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt  \
    && rm requirements.txt

COPY ./ctla /usr/src/ctla

ENTRYPOINT ["python", "/usr/src/ctla"]

# Extension: run hourly as cron job
FROM oneshot AS cron

COPY --chmod=755 <<EOF /etc/periodic/hourly/ctla.sh
#!/bin/sh
cd /app
exec python /usr/src/ctla
EOF

ENTRYPOINT ["crond", "-f"]
