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

from app.database.repositories.phone_repository import PhoneRepository
from app.database.repositories.user_repository import UserRepository
from app.models.domain.user import User
from app.models.schemas.user import UserResponse
from app.models.schemas.wrapper import WrapperResponse


@pytest.fixture(params=("", "value", "Token value", "JWT value", "Bearer value"))
def wrong_authorization_header(request) -> str:
    return request.param


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "api_method, route_name",
    (("GET", "user:get-user"), ("PATCH", "user:update-user")),
)
async def test_user_can_not_access_own_profile_if_not_logged_in(
        initialized_app: FastAPI,
        client: AsyncClient,
        test_user: User,
        api_method: str,
        route_name: str,
) -> None:
    response = await client.request(api_method, initialized_app.url_path_for(route_name))
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "api_method, route_name",
    (("GET", "user:get-user"), ("PATCH", "user:update-user")),
)
async def test_user_can_not_retrieve_own_profile_if_wrong_token(
        initialized_app: FastAPI,
        client: AsyncClient,
        test_user: User,
        api_method: str,
        route_name: str,
        wrong_authorization_header: str,
) -> None:
    response = await client.request(
        api_method,
        initialized_app.url_path_for(route_name),
        headers={"Authorization": wrong_authorization_header},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_user_can_retrieve_own_profile(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_user: User, token: str
) -> None:
    response = await authorized_client.get(initialized_app.url_path_for("user:get-user"))
    assert response.status_code == status.HTTP_200_OK

    result = WrapperResponse(**response.json())
    assert result.success

    user_profile = UserResponse(**result.payload)
    assert user_profile.user.username == test_user.username


@pytest.mark.asyncio
async def test_user_can_update_username_on_own_profile(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        test_user: User,
        token: str,
        session,
) -> None:
    username = "new_username"

    phone_repository = PhoneRepository(session)
    verification_code = await phone_repository.create_verification_code_by_phone(test_user.phone)

    response = await authorized_client.patch(
        initialized_app.url_path_for("user:update-user"),
        json={"username": username, "verification_code": verification_code},
    )
    assert response.status_code == status.HTTP_200_OK

    result = WrapperResponse(**response.json())
    assert result.success

    user_profile = UserResponse(**result.payload).dict()
    assert user_profile["user"]["username"] == username


@pytest.mark.asyncio
async def test_user_can_update_phone_on_own_profile(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        test_user: User,
        token: str,
        session,
) -> None:
    phone = "+375257654322"

    phone_repository = PhoneRepository(session)
    verification_code = await phone_repository.create_verification_code_by_phone(phone)

    response = await authorized_client.patch(
        initialized_app.url_path_for("user:update-user"),
        json={"phone": phone, "verification_code": verification_code},
    )
    assert response.status_code == status.HTTP_200_OK

    result = WrapperResponse(**response.json())
    assert result.success

    user_profile = UserResponse(**result.payload).dict()
    assert user_profile["user"]["phone"] == phone


@pytest.mark.asyncio
async def test_user_can_change_password(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        test_user: User,
        session,
) -> None:
    password = "new_password"

    phone_repository = PhoneRepository(session)
    verification_code = await phone_repository.create_verification_code_by_phone(test_user.phone)

    response = await authorized_client.patch(
        initialized_app.url_path_for("user:update-user"),
        json={
            "password": password,
            "verification_code": verification_code
        },
    )
    assert response.status_code == status.HTTP_200_OK

    result = WrapperResponse(**response.json())
    assert result.success

    user_profile = UserResponse(**result.payload)

    user_repository = UserRepository(session)
    user = await user_repository.get_user_by_id(user_profile.user.id)

    assert user.check_password(password)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "credentials_part, credentials_value",
    (
            ("username", "taken_username"),
            ("phone", "+375257654323")
    ),
)
async def test_user_can_not_take_already_used_credentials(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        session,
        credentials_part: str,
        credentials_value: str,
) -> None:
    user_dict = {
        "username": "not_taken_username",
        "password": "password",
        "phone": "+375257654322"
    }
    user_dict.update({credentials_part: credentials_value})

    user_repository = UserRepository(session)
    await user_repository.create_user_by_phone(**user_dict)

    phone_repository = PhoneRepository(session)
    verification_code = await phone_repository.create_verification_code_by_phone(user_dict["phone"])

    response = await authorized_client.patch(
        initialized_app.url_path_for("user:update-user"),
        json={
            credentials_part: credentials_value,
            "verification_code": verification_code
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT
