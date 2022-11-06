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

from fastapi import APIRouter, Body, Depends, HTTPException, status, Response

from app.api.dependencies.database import get_repository
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.database.errors import EntityDoesNotExists, EntityCreateError
from app.database.repositories.users import UsersRepository
from app.database.repositories.verification_codes import VerificationRepository
from app.models.domain.user import UserInDB
from app.models.schemas.user import (
    UserInCreate,
    UserInLogin,
    UserWithToken,
    UserInResponseWithToken,
    PhoneInVerification,
)
from app.resources import strings
from app.services import jwt
from app.services.validate import check_username_is_taken, check_phone_is_valid, check_phone_is_taken
from app.services.sms import send_verify_code_to_phone

router = APIRouter()


@router.post(
    "/get_verification_code",
    status_code=status.HTTP_200_OK,
    name="auth:verification",
    response_class=Response
)
async def get_verification_code(
        verification: PhoneInVerification = Body(..., embed=True, alias="verification"),
        verification_repo: VerificationRepository = Depends(get_repository(VerificationRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> None:
    phone_number_invalid = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.PHONE_NUMBER_INVALID_ERROR
    )
    verification_service_unavailable = HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=strings.VERIFICATION_SERVICE_TEMPORARY_UNAVAILABLE
    )
    create_verification_code_error = HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=strings.VERIFICATION_CODE_CREATE_ERROR
    )
    phone_sms_send_error = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=strings.VERIFICATION_SERVICE_SEND_SMS_ERROR
    )

    if not check_phone_is_valid(verification.phone):
        raise phone_number_invalid

    code = await verification_repo.create_verification_code_by_phone(verification.phone)

    if not await send_verify_code_to_phone(settings.sms_server, verification.phone, code):
        raise phone_sms_send_error


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=UserInResponseWithToken,
    name="auth:register",
)
async def register(
        user_create: UserInCreate = Body(..., embed=True, alias="user"),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        verification_repo: VerificationRepository = Depends(get_repository(VerificationRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> UserInResponseWithToken:
    phone_invalid = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.PHONE_NUMBER_INVALID_ERROR
    )
    phone_taken = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.PHONE_TAKEN
    )
    username_taken = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.USERNAME_TAKEN
    )
    verification_code_wrong = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.VERIFICATION_CODE_IS_WRONG
    )
    user_create_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.USER_CREATE_ERROR
    )

    if not check_phone_is_valid(user_create.phone):
        raise phone_invalid

    if await check_phone_is_taken(users_repo, user_create.phone):
        raise phone_taken

    if await check_username_is_taken(users_repo, user_create.username):
        raise username_taken

    try:
        await verification_repo.get_verification_code_by_phone_and_code(
            user_create.phone,
            user_create.verification_code
        )
    except EntityDoesNotExists as exception:
        raise verification_code_wrong from exception

    try:
        user = await users_repo.create_user(
            username=user_create.username,
            phone=user_create.phone,
            password=user_create.password
        )
    except EntityCreateError as exception:
        raise user_create_error from exception

    try:
        await verification_repo.mark_as_verified_by_phone_and_verification_code(
            user_create.phone, user_create.verification_code
        )
    except EntityDoesNotExists as exception:
        raise verification_code_wrong from exception

    token = jwt.create_access_token_for_user(
        user_id=user.id,
        username=user.username,
        phone=user.phone,
        secret_key=settings.secret_key.get_secret_value()
    )

    return UserInResponseWithToken(user=UserWithToken(token=token, **user.__dict__))


@router.post(
    "/login",
    response_model=UserInResponseWithToken,
    name="auth:login",
)
async def login(
        user_login: UserInLogin = Body(..., embed=True, alias="user"),
        users_repo: UsersRepository = Depends(get_repository(UsersRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> UserInResponseWithToken:
    incorrect_credentials = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.INCORRECT_LOGIN_INPUT
    )

    try:
        user: UserInDB = await users_repo.get_user_by_username(user_login.username)
    except EntityDoesNotExists as exception:
        raise incorrect_credentials from exception

    if not user.check_password(user_login.password):
        raise incorrect_credentials

    token = jwt.create_access_token_for_user(
        user_id=user.id,
        username=user.username,
        phone=user.phone,
        secret_key=settings.secret_key.get_secret_value()
    )

    return UserInResponseWithToken(user=UserWithToken(token=token, **user.__dict__))
