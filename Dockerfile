FROM python:3.8

COPY ./requirements.txt .
RUN pip install -r requirements.txt

RUN apt update \
    && apt install -v libpq-dev gcc

RUN pip install psycopg2

WORKDIR /code
COPY . /code/
