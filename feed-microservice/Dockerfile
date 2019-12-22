FROM tiangolo/uvicorn-gunicorn:python3.7-alpine3.8
WORKDIR /app

RUN apk add --no-cache gcc musl-dev linux-headers make
RUN pip install -U setuptools pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
x
