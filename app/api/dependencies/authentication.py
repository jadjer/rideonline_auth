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

from loguru import logger
from typing import Callable, Optional

from fastapi import Depends, HTTPException, Security, requests, status
from fastapi.security import APIKeyHeader
from fastapi.exceptions import HTTPException as FastApiHTTPException

from app.api.dependencies.database import get_repository
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.database.repositories import UserRepository
from app.models.domain.user import User
from app.resources import strings
from app.services import jwt

HEADER_KEY = "Authorization"


class MyApiKeyHeader(APIKeyHeader):
    async def __call__(self, request: requests.Request) -> Optional[str]:
        try:
            return await super().__call__(request)
        except FastApiHTTPException as exception:
            logger.error(exception)
            raise HTTPException(status_code=exception.status_code, detail=strings.AUTHENTICATION_REQUIRED)


def get_current_user_authorizer() -> Callable:
    return _get_current_user


def get_current_user_id_authorizer() -> Callable:
    return _get_current_user_id


def _get_authorization_header(
        api_key: str = Security(MyApiKeyHeader(name=HEADER_KEY)),
        settings: AppSettings = Depends(get_app_settings),
) -> str:
    wrong_token_prefix = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=strings.WRONG_TOKEN_PREFIX
    )

    try:
        token_prefix, token = api_key.split(" ")
    except ValueError as exception:
        logger.error(exception)
        raise wrong_token_prefix from exception

    if token_prefix != settings.jwt_token_prefix:
        raise wrong_token_prefix

    return token


async def _get_current_user_username(
        token: str = Depends(_get_authorization_header),
        settings: AppSettings = Depends(get_app_settings),
) -> str:
    malformed_payload = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=strings.MALFORMED_PAYLOAD
    )

    try:
        user_id = jwt.get_username_from_token(token, settings.secret_key.get_secret_value())
    except ValueError as exception:
        logger.error(exception)
        raise malformed_payload from exception

    return user_id


async def _get_current_user(
        username: str = Depends(_get_current_user_username),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> User:
    user: User | None = await user_repository.get_user_by_username(username)
    if user:
        return user

    logger.error("User not found")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=strings.MALFORMED_PAYLOAD)
