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

from app.models.domain.user import User


@pytest.mark.asyncio
async def test_username_exists(initialized_app: FastAPI, client: AsyncClient, test_user: User):
    request_json = {"username": "username"}

    response = await client.post(initialized_app.url_path_for("exist:username"), json=request_json)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_username_does_not_exist(initialized_app: FastAPI, client: AsyncClient):
    request_json = {"username": "username"}

    response = await client.post(initialized_app.url_path_for("exist:username"), json=request_json)

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_phone_exists(initialized_app: FastAPI, client: AsyncClient, test_user: User):
    request_json = {"phone": "+375257654321"}

    response = await client.post(initialized_app.url_path_for("exist:phone"), json=request_json)

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_phone_does_not_exist(initialized_app: FastAPI, client: AsyncClient):
    request_json = {"phone": "+375257654321"}

    response = await client.post(initialized_app.url_path_for("exist:phone"), json=request_json)

    assert response.status_code == status.HTTP_404_NOT_FOUND
