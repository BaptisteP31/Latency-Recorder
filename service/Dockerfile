FROM python:3.13.3-alpine3.21

WORKDIR /app
COPY requirements.txt .
RUN apk update && apk add mariadb-connector-c-dev gcc musl-dev libffi-dev
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .

CMD ["python", "main.py"]