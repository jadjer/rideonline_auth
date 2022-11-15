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

from app.models.domain.profile import Profile
from app.models.domain.user import User
from app.models.schemas.profile import ProfileResponse
from app.models.schemas.wrapper import WrapperResponse


@pytest.mark.asyncio
async def test_unregistered_user_will_receive_profile(
        initialized_app: FastAPI, client: AsyncClient, test_user: User, test_profile: Profile
) -> None:

    response = await client.get(
        initialized_app.url_path_for("profiles:get-profile-by-id", user_id=test_user.id)
    )
    assert response.status_code == status.HTTP_200_OK

    result = WrapperResponse(**response.json())
    assert result.success

    profile = ProfileResponse(**result.payload)
    assert profile.user.id == test_user.id
    assert profile.user.username == test_user.username
    assert profile.user.phone == test_user.phone
    assert profile.profile.first_name == test_profile.first_name
    assert profile.profile.last_name == test_profile.last_name
    assert profile.profile.age == test_profile.age
    assert profile.profile.gender == test_profile.gender


@pytest.mark.asyncio
async def test_unregistered_user_can_not_retrieve_not_existing_profile(
        initialized_app: FastAPI, client: AsyncClient
) -> None:

    response = await client.get(
        initialized_app.url_path_for("profiles:get-profile-by-id", user_id=999999999999)
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_user_will_receive_profile(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_user: User, test_profile: Profile
) -> None:

    response = await authorized_client.get(
        initialized_app.url_path_for("profiles:get-profile-by-id", user_id=test_user.id)
    )
    assert response.status_code == status.HTTP_200_OK

    result = WrapperResponse(**response.json())
    assert result.success

    profile = ProfileResponse(**result.payload)
    assert profile.user.id == test_user.id
    assert profile.user.username == test_user.username
    assert profile.user.phone == test_user.phone
    assert profile.profile.first_name == test_profile.first_name
    assert profile.profile.last_name == test_profile.last_name
    assert profile.profile.age == test_profile.age
    assert profile.profile.gender == test_profile.gender


@pytest.mark.asyncio
async def test_user_can_not_retrieve_not_existing_profile(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_user: User, test_profile: Profile
) -> None:

    response = await authorized_client.get(
        initialized_app.url_path_for("profiles:get-profile-by-id", user_id=999999999999)
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
