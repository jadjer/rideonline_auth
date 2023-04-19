FROM python

ARG VERSION

ENV VERSION=${VERSION}
ENV DATABASE_HOST="192.168.100.9"
ENV DATABASE_USER="neo4j"
ENV DATABASE_PASS=""
ENV SMS_SERVICE="http://192.168.100.6"
ENV PUBLIC_KEY_PATH=""
ENV PRIVATE_KEY_PATH=""

#Generate keys
RUN mkdir -p /app/keys
WORKDIR /app/keys
COPY keys/generate_keys.sh /app/keys/generate_keys.sh
RUN chmod +x generate_keys.sh
RUN sh generate_keys.sh
VOLUME /app/keys

RUN mkdir -p /app/app
WORKDIR /app
RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY app /app/app

EXPOSE 8000

ENTRYPOINT ["uvicorn", "app.app:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
