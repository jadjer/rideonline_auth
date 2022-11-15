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

import pytest

from fastapi import FastAPI, status
from httpx import AsyncClient

from app.database.repositories.user_repository import UserRepository
from app.database.repositories.phone_repository import PhoneRepository
from app.models.domain.user import User, UserInDB
from app.models.schemas.wrapper import WrapperResponse


@pytest.mark.asyncio
async def test_user_success_registration(initialized_app: FastAPI, client: AsyncClient, session):
    phone = "+375257654321"
    username = "username"
    password = "password"

    verification_repo = PhoneRepository(session)
    verification_code = await verification_repo.create_verification_code_by_phone(phone)

    registration_json = {
        "username": username,
        "phone": phone,
        "password": password,
        "verification_code": verification_code
    }

    response = await client.post(initialized_app.url_path_for("auth:register"), json=registration_json)
    assert response.status_code == status.HTTP_201_CREATED

    result = WrapperResponse(**response.json())
    assert result.success

    user_repository = UserRepository(session)
    user = await user_repository.get_user_by_username(username=username)

    assert user.username == username
    assert user.phone == phone
    assert user.check_password(password)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "credentials_part, credentials_value",
    (
            ("username", "free_username"),
            ("phone", "+375257654322")
    ),
)
async def test_failed_user_registration_when_some_credentials_are_taken(
        initialized_app: FastAPI,
        client: AsyncClient,
        test_user: User,
        session,
        credentials_part: str,
        credentials_value: str,
) -> None:
    phone = "+375257654321"

    phone_repository = PhoneRepository(session)
    verification_code = await phone_repository.create_verification_code_by_phone(phone)

    registration_json = {
        "username": "username",
        "phone": phone,
        "password": "password",
        "verification_code": verification_code,
        credentials_part: credentials_value
    }

    response = await client.post(
        initialized_app.url_path_for("auth:register"), json=registration_json
    )

    assert response.status_code == status.HTTP_409_CONFLICT
