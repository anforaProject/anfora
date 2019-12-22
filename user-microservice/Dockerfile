FROM python:3.7.4-alpine

RUN pip install pipenv
RUN pip install -U setuptools pip
RUN apk add --no-cache postgresql-libs postgresql-dev
RUN apk add --no-cache --virtual .build-deps gcc musl-dev openssl-dev libffi-dev git
RUN apk add --no-cache make
RUN apk add build-base python-dev py-pip jpeg-dev zlib-dev
ENV LIBRARY_PATH=/lib:/usr/lib
COPY Pipfile* /tmp/
RUN cd /tmp && pipenv lock --requirements > requirements.txt
RUN cd /tmp && pip install -r requirements.txt
COPY . /tmp/myapp
RUN cd /tmp/myapp/src
CMD ["gunicorn" "-w" "4" "-b" "127.0.0.1:$PORT" "-k" "uvicorn.workers.UvicornWorker" "server:app"]
