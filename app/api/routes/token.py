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

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.database import get_repository
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.database.repositories.token_repository import TokenRepository
from app.database.repositories.user_repository import UserRepository
from app.models.domain.token import Token
from app.models.schemas.user import UserLogin
from app.models.schemas.wrapper import WrapperResponse
from app.resources import strings
from app.services.token import create_tokens_for_user, get_user_id_from_refresh_token

router = APIRouter()


@router.post("/get", status_code=status.HTTP_200_OK, name="token:get-token")
async def get_token(
        request: UserLogin,
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
        token_repository: TokenRepository = Depends(get_repository(TokenRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> WrapperResponse:
    user = await user_repository.get_user_by_username(request.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.USER_DOES_NOT_EXIST_ERROR)

    if not user.check_password(request.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.INCORRECT_LOGIN_INPUT)

    token_access, token_refresh = create_tokens_for_user(
        user_id=user.id,
        username=user.username,
        phone=user.phone,
        secret_key=settings.secret_key.get_secret_value()
    )

    await token_repository.update_token(user.id, token_refresh)

    return WrapperResponse(
        payload=Token(token_access=token_access, token_refresh=token_refresh)
    )


@router.post("/refresh", status_code=status.HTTP_200_OK, name="token:refresh-token")
async def refresh_token(
        request: Token,
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
        token_repository: TokenRepository = Depends(get_repository(TokenRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> WrapperResponse:
    user_id = get_user_id_from_refresh_token(
        request.token_access,
        request.token_refresh,
        settings.secret_key.get_secret_value()
    )

    if not user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.WRONG_TOKEN_PAIR)

    user_token = await token_repository.get_token(user_id)
    if request.token_refresh != user_token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.REFRESH_TOKEN_IS_REVOKED)

    user = await user_repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.USER_DOES_NOT_EXIST_ERROR)

    token_access, token_refresh = create_tokens_for_user(
        user_id=user.id,
        username=user.username,
        phone=user.phone,
        secret_key=settings.secret_key.get_secret_value()
    )

    await token_repository.update_token(user.id, token_refresh)

    return WrapperResponse(
        payload=Token(token_access=token_access, token_refresh=token_refresh)
    )
