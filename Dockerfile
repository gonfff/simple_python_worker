FROM python:3.6-alpine

COPY pip/pip.conf /etc/pip.conf
COPY pip/nexus.pem /etc/nexus.pem

COPY ./ /app/
RUN apk update && apk add --no-cache postgresql-libs &&  \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev libressl-dev libffi-dev make && \
 pip install -r /app/requirements.txt --no-cache-dir && \
 apk --purge del .build-deps
RUN pip install -e /app

ENTRYPOINT lti_octopoda