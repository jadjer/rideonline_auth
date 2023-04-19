FROM python

ARG VERSION

ENV VERSION=${VERSION}
ENV DATABASE_HOST=""
ENV DATABASE_USER=""
ENV DATABASE_PASS=""
ENV SMS_SERVICE=""

ENV BASE_PATH=/app
ENV APP_PATH=$BASE_PATH/app
ENV KEY_PATH=$BASE_PATH/keys

ENV PUBLIC_KEY_PATH="$KEY_PATH/public_key.pem"
ENV PRIVATE_KEY_PATH="$KEY_PATH/private_key.pem"

RUN pip install --upgrade pip

RUN mkdir -p $KEY_PATH
WORKDIR $BASE_PATH
COPY generate_keys.sh $BASE_PATH
VOLUME $KEY_PATH
RUN chmod +x $BASE_PATH/generate_keys.sh
RUN sh $BASE_PATH/generate_keys.sh $KEY_PATH

RUN mkdir -p $APP_PATH
WORKDIR $BASE_PATH
COPY requirements.txt $BASE_PATH
RUN pip install --no-cache-dir --upgrade -r $BASE_PATH/requirements.txt
COPY app $APP_PATH

EXPOSE 8000

ENTRYPOINT ["uvicorn", "app.app:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
