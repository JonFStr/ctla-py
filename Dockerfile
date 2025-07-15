FROM python:3
LABEL authors="Jonathan Straub"

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt  \
    && rm requirements.txt

COPY ./ctla /usr/src/ctla

ENTRYPOINT ["python", "/usr/src/ctla"]