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

from fastapi import APIRouter, Body, Depends, HTTPException, status

from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.database.repositories import UserRepository, PhoneRepository
from app.models.domain.user import User
from app.models.schemas.user import (
    UserCreate,
    UserLogin,
    UserWithToken,
    UserResponseWithToken,
    PhoneVerification,
)
from app.services import jwt
from app.services.validate import check_phone_is_valid
from app.services.sms import send_verify_code_to_phone
from app.api.dependencies.database import get_repository
from app.resources import strings

router = APIRouter()


@router.post("/get_verification_code", status_code=status.HTTP_200_OK, name="auth:verification")
async def get_verification_code(
        verification: PhoneVerification = Body(..., embed=True, alias="verification"),
        phone_repository: PhoneRepository = Depends(get_repository(PhoneRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> None:
    if not check_phone_is_valid(verification.phone):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.PHONE_NUMBER_INVALID_ERROR)

    code = await phone_repository.create_verification_code(verification.phone)

    if not await send_verify_code_to_phone(settings.sms_server, verification.phone, code):
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=strings.SEND_SMS_ERROR)


@router.post("/register", name="auth:register")
async def register(
        user_create: UserCreate = Body(..., embed=True, alias="user"),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
        phone_repository: PhoneRepository = Depends(get_repository(PhoneRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> UserResponseWithToken:
    if await user_repository.is_exists(user_create.username):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.USERNAME_TAKEN)

    if await phone_repository.is_attached(user_create.phone):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.PHONE_NUMBER_TAKEN)

    if not await phone_repository.verify_code(user_create.phone, user_create.verification_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.VERIFICATION_CODE_IS_WRONG)

    user: User | None = await user_repository.create_user(user_create.username, user_create.phone)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USER_CREATE_ERROR)

    token = jwt.create_access_token_for_user(username=user.username, secret_key=settings.secret_key.get_secret_value())

    return UserResponseWithToken(user=UserWithToken(token=token, username=user_create.username))


@router.post("/login", response_model=UserResponseWithToken, name="auth:login")
async def login(
        user_login: UserLogin = Body(..., embed=True, alias="user"),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
        phone_repository: PhoneRepository = Depends(get_repository(PhoneRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> UserResponseWithToken:
    if not await phone_repository.verify_code(user_login.phone, user_login.verification_code):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.VERIFICATION_CODE_IS_WRONG)

    user: User | None = await user_repository.get_user_by_phone(user_login.phone)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.INCORRECT_LOGIN_INPUT)

    token = jwt.create_access_token_for_user(username=user.username, secret_key=settings.secret_key.get_secret_value())

    return UserResponseWithToken(user=UserWithToken(token=token, username=user.username))
