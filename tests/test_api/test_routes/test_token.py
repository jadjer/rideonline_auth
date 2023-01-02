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

from app.models.domain.user import User


@pytest.mark.asyncio
async def test_user_can_get_new_tokens(
        initialized_app: FastAPI,
        client: AsyncClient,
        test_user: User
) -> None:
    username = "username"
    password = "password"

    response = await client.post(
        initialized_app.url_path_for("tokens:get-token"),
        json={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_user_can_not_get_new_tokens_for_wrong_credentials(
        initialized_app: FastAPI,
        client: AsyncClient,
) -> None:
    username = "username"
    password = "password"

    response = await client.post(
        initialized_app.url_path_for("tokens:get-token"),
        json={
            "username": username,
            "password": password,
        },
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_user_refresh_token(
        initialized_app: FastAPI,
        client: AsyncClient,
        tokens: (str, str)
) -> None:
    token_access, token_refresh = tokens

    response = await client.post(
        initialized_app.url_path_for("tokens:refresh-token"),
        json={
            "token_access": token_access,
            "token_refresh": token_refresh,
        },
    )

    assert response.status_code == status.HTTP_200_OK
