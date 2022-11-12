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
    create_access_token_for_user,
    get_username_from_token,
    create_access_token,
    get_phone_from_token,
)


def test_creating_jwt_token() -> None:
    token = create_access_token(
        data={"content": "payload"},
        secret_key="secret",
        expires_delta=timedelta(minutes=1),
    )
    parsed_payload = jwt.decode(token, "secret", algorithms=[ALGORITHM])

    assert parsed_payload["content"] == "payload"


@pytest.mark.asyncio
async def test_creating_token_for_user(test_user: User):
    token = create_access_token_for_user(
        user_id=test_user.id,
        username=test_user.username,
        phone=test_user.phone,
        secret_key="secret"
    )
    parsed_payload = jwt.decode(token, "secret", algorithms=[ALGORITHM])

    assert parsed_payload["username"] == test_user.username


@pytest.mark.asyncio
async def test_retrieving_token_from_user(test_user: User):
    token = create_access_token_for_user(
        user_id=test_user.id,
        username=test_user.username,
        phone=test_user.phone,
        secret_key="secret"
    )

    username = get_username_from_token(token, "secret")
    assert username == test_user.username

    phone = get_phone_from_token(token, "secret")
    assert phone == test_user.phone


def test_error_when_wrong_token():
    with pytest.raises(ValueError):
        get_username_from_token("asdf", "asdf")


def test_error_when_wrong_token_shape():
    token = create_access_token(
        data={"content": "payload"},
        secret_key="secret",
        expires_delta=timedelta(minutes=1),
    )
    with pytest.raises(ValueError):
        get_username_from_token(token, "secret")
