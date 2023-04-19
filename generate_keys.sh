#!/usr/bin/env sh

KEY_DIR=$1

if [ ! -d "$KEY_DIR" ]; then
  mkdir -p "$KEY_DIR";
fi

PUBLIC_KEY="$KEY_DIR/public_key.pem"
PRIVATE_KEY="$KEY_DIR/private_key.pem"

openssl genpkey -algorithm RSA -out "$PRIVATE_KEY"
openssl rsa -pubout -in "$PRIVATE_KEY" -out "$PUBLIC_KEY"
