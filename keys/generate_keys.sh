#!/usr/bin/env sh

PUBLIC_KEY=public_key.pem
PRIVATE_KEY=private_key.pem

openssl genpkey -algorithm RSA -out $PRIVATE_KEY
openssl rsa -pubout -in $PRIVATE_KEY -out $PUBLIC_KEY
