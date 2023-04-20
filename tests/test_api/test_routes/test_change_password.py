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

from fastapi import FastAPI, status
from httpx import AsyncClient

from app.database.repositories.phone_repository import PhoneRepository
from app.models.domain.user import User


@pytest.mark.asyncio
async def test_user_success_change_password_without_auth(initialized_app, client, test_user, session):
    phone = "+375257654321"
    password = "password"

    phone_repository = PhoneRepository(session)
    verification_code, phone_token = await phone_repository.create_verification_code_by_phone(phone)

    change_password_json = {
        "phone": phone,
        "password": password,
        "verification_code": verification_code,
        "phone_token": phone_token,
    }

    response = await client.post(initialized_app.url_path_for("auth:change-password"), json=change_password_json)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_unregistered_user_can_not_change_password_without_auth(initialized_app, client, session):
    phone = "+375257654321"
    password = "password"

    phone_repository = PhoneRepository(session)
    verification_code, phone_token = await phone_repository.create_verification_code_by_phone(phone)

    change_password_json = {
        "phone": phone,
        "password": password,
        "verification_code": verification_code,
        "phone_token": phone_token,
    }

    response = await client.post(initialized_app.url_path_for("auth:change-password"), json=change_password_json)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_user_success_change_password(initialized_app: FastAPI, authorized_client: AsyncClient, test_user: User):
    change_password_json = {
        "password": "password",
    }

    response = await authorized_client.patch(
        initialized_app.url_path_for("users:update-current-user"),
        json=change_password_json
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_unregistered_user_can_not_change_password(initialized_app: FastAPI, client: AsyncClient):
    change_password_json = {
        "password": "password",
    }

    response = await client.patch(initialized_app.url_path_for("users:update-current-user"), json=change_password_json)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
