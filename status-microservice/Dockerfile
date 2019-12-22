FROM python:3.7.4-alpine

RUN pip install pipenv
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN \
 apk add --no-cache postgresql-libs && \
 apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev
RUN cd /tmp && pip install -r requirements.txt
COPY . /tmp/myapp
RUN cd /tmp/myapp/src
CMD ["gunicorn" "-w" "4" "-b" "127.0.0.1:$PORT" "-k" "uvicorn.workers.UvicornWorker" "server:app"]
