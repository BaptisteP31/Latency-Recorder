FROM python:3.13.3-alpine3.21

WORKDIR /app
COPY app.py .
COPY templates/ ./templates/
RUN apk update && apk add mariadb-connector-c-dev gcc musl-dev libffi-dev
RUN pip install flask mariadb

CMD ["python", "app.py"]