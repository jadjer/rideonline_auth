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

from fastapi import status

from app.services.token import create_tokens_for_user


@pytest.mark.asyncio
async def test_unable_to_login_with_wrong_jwt_prefix(app, client, tokens):
    token_access, _ = tokens
    response = await client.get(
        app.url_path_for("users:get-user"),
        headers={"Authorization": f"WrongPrefix {token_access}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_unable_to_login_when_user_does_not_exist_any_more(settings, initialized_app, client, authorization_prefix):
    token_access, _ = create_tokens_for_user(
        user_id=9999999999999,
        username="test_user",
        secret_key=settings.private_key,
    )
    response = await client.get(
        initialized_app.url_path_for("users:get-user"),
        headers={"Authorization": f"{authorization_prefix} {token_access}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
