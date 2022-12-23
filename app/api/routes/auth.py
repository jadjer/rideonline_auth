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

from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.database.repositories.phone_repository import PhoneRepository
from app.database.repositories.user_repository import UserRepository
from app.models.domain.user import User
from app.models.schemas.phone import (
    PhoneVerification,
    PhoneToken,
)
from app.models.schemas.user import (
    UserCreate,
    UserLogin,
    UserWithTokenResponse,
    Token,
)
from app.models.schemas.wrapper import WrapperResponse
from app.services.token import create_tokens_for_user
from app.services.validate import check_phone_is_valid
from app.services.sms import send_verify_code_to_phone
from app.api.dependencies.database import get_repository
from app.resources import strings

router = APIRouter()


@router.post("/get_verification_code", status_code=status.HTTP_200_OK, name="auth:verification")
async def get_verification_code(
        request: PhoneVerification,
        phone_repository: PhoneRepository = Depends(get_repository(PhoneRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> WrapperResponse:
    if not check_phone_is_valid(request.phone):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.PHONE_NUMBER_INVALID_ERROR)

    verification_code, token = await phone_repository.create_verification_code_by_phone(request.phone)

    if not await send_verify_code_to_phone(settings.sms_service, request.phone, verification_code):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=strings.SEND_SMS_ERROR)

    return WrapperResponse(
        payload=PhoneToken(
            token=token
        )
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, name="auth:register")
async def register(
        request: UserCreate,
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
        phone_repository: PhoneRepository = Depends(get_repository(PhoneRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> WrapperResponse:
    if await user_repository.is_exists(request.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.USERNAME_TAKEN)

    if await phone_repository.is_attached_by_phone(request.phone):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.PHONE_NUMBER_TAKEN)

    if not await phone_repository.verify_phone_by_code_and_token(
            request.phone, request.verification_code, request.phone_token,
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.VERIFICATION_CODE_IS_WRONG)

    user = await user_repository.create_user_by_phone(**request.__dict__)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USER_CREATE_ERROR)

    token_access, token_refresh = create_tokens_for_user(
        user_id=user.id,
        username=user.username,
        phone=user.phone,
        secret_key=settings.secret_key.get_secret_value()
    )

    return WrapperResponse(
        payload=UserWithTokenResponse(
            user=User(id=user.id, phone=user.phone, username=user.username, is_blocked=user.is_blocked),
            token=Token(token_access=token_access, token_refresh=token_refresh)
        )
    )


@router.post("/login", status_code=status.HTTP_200_OK, name="auth:login")
async def login(
        request: UserLogin,
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
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

    return WrapperResponse(
        payload=UserWithTokenResponse(
            user=User(id=user.id, phone=user.phone, username=user.username, is_blocked=user.is_blocked),
            token=Token(token_access=token_access, token_refresh=token_refresh)
        )
    )
