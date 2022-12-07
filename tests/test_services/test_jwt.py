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

from datetime import timedelta

from jose import jwt
import pytest

from app.models.domain.user import User
from app.services.token import (
    ALGORITHM,
    JWT_ACCESS_SUBJECT,
    JWT_REFRESH_SUBJECT,
    create_access_token,
    create_refresh_token,
    create_tokens_for_user,
    get_user_id_from_access_token,
    get_user_id_from_refresh_token
)


def test_creating_jwt_tokens() -> None:
    token = create_access_token(
        data={"content": "payload"},
        secret_key="secret",
        subject=JWT_ACCESS_SUBJECT,
        expires_delta=timedelta(minutes=1),
    )
    parsed_payload = jwt.decode(token, "secret", algorithms=[ALGORITHM])

    assert parsed_payload["content"] == "payload"


def test_creating_refresh_tokens() -> None:
    token = create_refresh_token(
        data={"content": "payload"},
        secret_key="secret",
        subject=JWT_REFRESH_SUBJECT,
        expires_delta=timedelta(minutes=1),
        access_token="token"
    )
    parsed_payload = jwt.decode(token, "secret", algorithms=[ALGORITHM], access_token="token")

    assert parsed_payload["content"] == "payload"


def test_creating_access_token_for_user(test_user: User):
    token_access, _ = create_tokens_for_user(
        user_id=test_user.id,
        username=test_user.username,
        phone=test_user.phone,
        secret_key="secret"
    )
    parsed_payload = jwt.decode(token_access, "secret", algorithms=[ALGORITHM])

    assert parsed_payload["user_id"] == test_user.id
    assert parsed_payload["username"] == test_user.username
    assert parsed_payload["phone"] == test_user.phone


def test_creating_refresh_token_for_user(test_user: User):
    token_access, token_refresh = create_tokens_for_user(
        user_id=test_user.id,
        username=test_user.username,
        phone=test_user.phone,
        secret_key="secret"
    )
    parsed_payload = jwt.decode(token_refresh, "secret", algorithms=[ALGORITHM], access_token=token_access)

    assert parsed_payload["user_id"] == test_user.id
    assert parsed_payload["username"] == test_user.username
    assert parsed_payload["phone"] == test_user.phone


def test_retrieving_access_token_from_user(test_user: User):
    token_access, _ = create_tokens_for_user(
        user_id=test_user.id,
        username=test_user.username,
        phone=test_user.phone,
        secret_key="secret"
    )

    user_id = get_user_id_from_access_token(token_access, "secret")
    assert user_id == test_user.id


def test_retrieving_refresh_token_from_user(test_user: User):
    token_access, token_refresh = create_tokens_for_user(
        user_id=test_user.id,
        username=test_user.username,
        phone=test_user.phone,
        secret_key="secret"
    )

    user_id = get_user_id_from_refresh_token(token_access, token_refresh, "secret")
    assert user_id == test_user.id


def test_error_when_wrong_token():
    with pytest.raises(ValueError):
        get_user_id_from_access_token("asdf", "asdf")


def test_error_when_wrong_token_shape():
    token = create_access_token(
        data={"content": "payload"},
        secret_key="secret",
        subject=JWT_ACCESS_SUBJECT,
        expires_delta=timedelta(minutes=1),
    )
    with pytest.raises(ValueError):
        get_user_id_from_access_token(token, "secret")
