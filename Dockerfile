FROM python

ARG VERSION

ENV VERSION=${VERSION}
ENV DATABASE_HOST="192.168.100.9"
ENV DATABASE_USER="neo4j"
ENV DATABASE_PASS=""
ENV SMS_SERVER="http://192.168.100.6"
ENV SECRET_KEY=""

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY app /app/app

EXPOSE 8000

CMD ["uvicorn", "app.app:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]