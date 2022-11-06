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

from typing import Callable, Optional

from fastapi import Depends, HTTPException, Security, requests, status
from fastapi.security import APIKeyHeader
from fastapi.exceptions import HTTPException as FastapiHTTPException

from app.api.dependencies.database import get_repository
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.database.errors import EntityDoesNotExists
from app.database.repositories.users import UsersRepository
from app.models.domain.user import User
from app.resources import strings
from app.services import jwt

HEADER_KEY = "x-api-key"


class ApiKeyHeader(APIKeyHeader):
    async def __call__(self, request: requests.Request) -> Optional[str]:
        try:
            return await super().__call__(request)
        except FastapiHTTPException as original_auth_exc:
            raise HTTPException(status_code=original_auth_exc.status_code, detail=strings.AUTHENTICATION_REQUIRED)


def get_current_user_authorizer() -> Callable:  # type: ignore
    return _get_current_user


def _get_authorization_header(
        api_key: str = Security(ApiKeyHeader(name=HEADER_KEY)),
        settings: AppSettings = Depends(get_app_settings),
) -> str:
    try:
        token_prefix, token = api_key.split(" ")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.WRONG_TOKEN_PREFIX,
        )
    if token_prefix != settings.jwt_token_prefix:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.WRONG_TOKEN_PREFIX,
        )

    return token


async def _get_current_user(
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        token: str = Depends(_get_authorization_header),
        settings: AppSettings = Depends(get_app_settings),
) -> User:
    try:
        email = jwt.get_email_from_token(
            token,
            str(settings.secret_key.get_secret_value()),
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.MALFORMED_PAYLOAD,
        )

    try:
        return await users_repo.get_user_by_email(email=email)
    except EntityDoesNotExists:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.MALFORMED_PAYLOAD,
        )
