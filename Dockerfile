FROM python:3.8-alpine

COPY requirements.txt /app/requirements.txt

RUN apk update && apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install -r /app/requirements.txt --no-cache-dir && \
    apk --purge del .build-deps
COPY ./ /app
RUN pip install -e /app
RUN apk add bash
CMD simple_worker


### test env
#ENV DATABASE_NAME simple_database
#ENV DATABASE_USERNAME postgres
#ENV DATABASE_PASSWORD postgres
#ENV DATABASE_HOST host.docker.internal
#ENV DATABASE_PORT 5432