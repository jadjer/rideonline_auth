#  Copyright 2022 Pavel Suprunov
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from datetime import datetime, timedelta

from jose import JWTError, jwt
from pydantic import ValidationError

from app.models.schemas.jwt import JWTMeta, JWTUser

JWT_SUBJECT = "access"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10


def create_access_token(data: dict, secret_key: str, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=10)
    to_encode.update(JWTMeta(exp=expire, sub=JWT_SUBJECT).dict())
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    return encoded_jwt


def create_access_token_for_user(user_id: int, username: str, phone: str, secret_key: str) -> str:
    jwt_user = JWTUser(user_id=user_id, username=username, phone=phone)
    return create_access_token(
        data=jwt_user.__dict__,
        secret_key=secret_key,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def get_username_from_token(token: str, secret_key: str) -> str:
    try:
        return JWTUser(**jwt.decode(token, secret_key, algorithms=[ALGORITHM])).username
    except JWTError as decode_error:
        raise ValueError("unable to decode JWT token") from decode_error
    except ValidationError as validation_error:
        raise ValueError("malformed payload in token") from validation_error


def get_phone_from_token(token: str, secret_key: str) -> str:
    try:
        return JWTUser(**jwt.decode(token, secret_key, algorithms=[ALGORITHM])).phone
    except JWTError as decode_error:
        raise ValueError("unable to decode JWT token") from decode_error
    except ValidationError as validation_error:
        raise ValueError("malformed payload in token") from validation_error
