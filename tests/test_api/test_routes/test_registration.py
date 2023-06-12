#  Copyright 2022 Pavel Suprunov
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import pytest

from fastapi import status

from app.database.repositories.user_repository import UserRepository
from app.database.repositories.phone_repository import PhoneRepository
from app.models.domain.verification_code import VerificationCode
from app.models.schemas.wrapper import WrapperResponse
from app.services.verification_code import create_verification_code


@pytest.mark.asyncio
async def test_user_success_registration(initialized_app, client, session, verification_code):
    phone = "+375257654321"
    username = "username"
    password = "password"

    phone_repository = PhoneRepository(session)
    await phone_repository.update_verification_code_by_phone(phone, verification_code.secret, verification_code.token, verification_code.code)

    registration_json = {
        "phone": phone,
        "username": username,
        "password": password,
        "verification_token": verification_code.token,
        "verification_code": verification_code.code,
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
async def test_failed_user_registration_when_username_are_taken(initialized_app, client, session, test_user, verification_code):
    phone = "+375257654322"

    phone_repository = PhoneRepository(session)
    await phone_repository.update_verification_code_by_phone(phone, verification_code.secret, verification_code.token, verification_code.code)

    registration_json = {
        "phone": phone,
        "username": "username",
        "password": "password",
        "verification_token": verification_code.token,
        "verification_code": verification_code.code,
    }

    response = await client.post(initialized_app.url_path_for("auth:register"), json=registration_json)

    assert response.status_code == status.HTTP_409_CONFLICT


@pytest.mark.asyncio
async def test_failed_user_registration_when_phone_are_taken(initialized_app, client, session, verification_code, test_user):
    phone = "+375257654321"

    phone_repository = PhoneRepository(session)
    await phone_repository.update_verification_code_by_phone(phone, verification_code.secret, verification_code.token, verification_code.code)

    registration_json = {
        "phone": phone,
        "username": "free_username",
        "password": "password",
        "verification_token": verification_code.token,
        "verification_code": verification_code.code,
    }

    response = await client.post(initialized_app.url_path_for("auth:register"), json=registration_json)

    assert response.status_code == status.HTTP_409_CONFLICT
