FROM python

ARG VERSION
ARG BUILD_DATE
ARG GITHUB_SHA

ENV VERSION=$VERSION
ENV BUILD_DATE=$BUILD_DATE
ENV GITHUB_SHA=$GITHUB_SHA

ENV DATABASE_HOST=""
ENV DATABASE_USER=""
ENV DATABASE_PASS=""
ENV SMS_SERVICE=""

ENV BASE_PATH="/app"
ENV APP_PATH="$BASE_PATH/app"
ENV KEY_PATH="$BASE_PATH/keys"

ENV PUBLIC_KEY_PATH="$KEY_PATH/public_key.pem"
ENV PRIVATE_KEY_PATH="$KEY_PATH/private_key.pem"

RUN pip install --upgrade pip

RUN mkdir -p $BASE_PATH
WORKDIR $BASE_PATH

RUN mkdir -p $KEY_PATH
VOLUME $KEY_PATH

RUN mkdir -p $APP_PATH
COPY requirements.txt $BASE_PATH
RUN pip install --no-cache-dir --upgrade -r $BASE_PATH/requirements.txt
COPY app $APP_PATH

EXPOSE 8000

ENTRYPOINT ["uvicorn", "app.app:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
