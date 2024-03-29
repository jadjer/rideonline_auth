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
from app.api.dependencies.get_from_header import get_language
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.database.repositories.phone_repository import PhoneRepository
from app.database.repositories.token_repository import TokenRepository
from app.database.repositories.user_repository import UserRepository
from app.models.domain.user import User
from app.models.domain.verification_code import VerificationCode
from app.models.schemas.phone import Phone, PhoneTokenResponse
from app.models.schemas.user import UserCreate, UserLogin, UserWithTokenResponse, Token, UserChangePassword
from app.models.schemas.wrapper import WrapperResponse
from app.services.token import create_tokens_for_user, get_user_id_from_refresh_token
from app.services.validate import check_phone_is_valid
from app.services.sms import send_verify_code_to_phone
from app.resources import strings_factory
from app.services.verification_code import create_verification_code, check_verification_code

router = APIRouter()


@router.post("/get_verification_code", status_code=status.HTTP_200_OK, name="auth:verification")
async def get_verification_code(
        request: Phone,
        language: str = Depends(get_language),
        phone_repository: PhoneRepository = Depends(get_repository(PhoneRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> WrapperResponse:
    async def generate_verification_code(phone: str) -> VerificationCode:
        verification: VerificationCode = create_verification_code(settings.verification_code_timeout)
        verification_message_template = strings.VERIFICATION_CODE_TEMPLATE
        verification_message = verification_message_template.format(code=verification.code)

        await phone_repository.update_verification_code_by_phone(phone, verification.secret, verification.token, verification.code)

        if not await send_verify_code_to_phone(settings.sms_service, phone, verification_message):
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, strings.SEND_SMS_ERROR)

        return verification

    strings = strings_factory.get_language(language)

    if not check_phone_is_valid(request.phone):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, strings.PHONE_NUMBER_INVALID_ERROR)

    verification_code: VerificationCode | None = await phone_repository.get_verification_code_by_phone(request.phone)
    if not verification_code:
        verification_code = await generate_verification_code(request.phone)

    if not check_verification_code(verification_code.secret, verification_code.token, verification_code.code, settings.verification_code_timeout):
        verification_code = await generate_verification_code(request.phone)

    return WrapperResponse(
        payload=PhoneTokenResponse(verification_token=verification_code.token)
    )


@router.post("/register", status_code=status.HTTP_201_CREATED, name="auth:register")
async def register(
        request: UserCreate,
        language: str = Depends(get_language),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
        phone_repository: PhoneRepository = Depends(get_repository(PhoneRepository)),
        token_repository: TokenRepository = Depends(get_repository(TokenRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> WrapperResponse:
    strings = strings_factory.get_language(language)

    verification_code: VerificationCode = await phone_repository.get_verification_code_by_phone(request.phone)
    if not verification_code:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, strings.VERIFICATION_CODE_DOES_NOT_EXISTS)

    if not check_verification_code(verification_code.secret, request.verification_token, request.verification_code, settings.verification_code_timeout):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, strings.VERIFICATION_CODE_IS_WRONG)

    if await phone_repository.is_attached_by_phone(request.phone):
        raise HTTPException(status.HTTP_409_CONFLICT, strings.PHONE_NUMBER_TAKEN)

    if await user_repository.is_exists(request.username):
        raise HTTPException(status.HTTP_409_CONFLICT, strings.USERNAME_TAKEN)

    user = await user_repository.create_user(**request.model_dump())
    if user:
        token_access, token_refresh = create_tokens_for_user(user.id, user.username, settings.private_key)

        await token_repository.update_token(user.id, token_refresh)

        return WrapperResponse(
            payload=UserWithTokenResponse(
                user=user,
                token=Token(token_access=token_access, token_refresh=token_refresh)
            )
        )

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.USER_CREATE_ERROR)


@router.post("/login", status_code=status.HTTP_200_OK, name="auth:login")
async def login(
        request: UserLogin,
        language: str = Depends(get_language),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
        token_repository: TokenRepository = Depends(get_repository(TokenRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> WrapperResponse:
    strings = strings_factory.get_language(language)

    user = await user_repository.get_user_by_username(request.username)

    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, strings.USER_DOES_NOT_EXIST_ERROR)

    if not user.check_password(request.password):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, strings.INCORRECT_LOGIN_INPUT)

    token_access, token_refresh = create_tokens_for_user(user.id, user.username, settings.private_key)

    await token_repository.update_token(user.id, token_refresh)

    return WrapperResponse(
        payload=UserWithTokenResponse(
            user=user,
            token=Token(token_access=token_access, token_refresh=token_refresh)
        )
    )


@router.post("/change_password", status_code=status.HTTP_200_OK, name="auth:change-password")
async def change_password(
        request: UserChangePassword,
        language: str = Depends(get_language),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
        phone_repository: PhoneRepository = Depends(get_repository(PhoneRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> WrapperResponse:
    strings = strings_factory.get_language(language)

    verification_code = await phone_repository.get_verification_code_by_phone(request.phone)
    if not verification_code:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, strings.VERIFICATION_CODE_IS_WRONG)

    if not check_verification_code(verification_code.secret, request.verification_token, request.verification_code, settings.verification_code_timeout):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, strings.VERIFICATION_CODE_IS_WRONG)

    if not await phone_repository.is_attached_by_phone(request.phone):
        raise HTTPException(status.HTTP_404_NOT_FOUND, strings.PHONE_NUMBER_DOES_NOT_EXIST)

    user = await user_repository.get_user_by_phone(request.phone)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, strings.USER_DOES_NOT_EXIST_ERROR)

    user = await user_repository.update_user_by_user_id(user.id, password=request.password)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, strings.USER_DOES_NOT_EXIST_ERROR)

    token_access, token_refresh = create_tokens_for_user(user.id, user.username, settings.private_key)

    return WrapperResponse(
        payload=UserWithTokenResponse(
            user=user,
            token=Token(token_access=token_access, token_refresh=token_refresh)
        )
    )


@router.post("/refresh_token", status_code=status.HTTP_200_OK, name="auth:refresh-token")
async def refresh_token(
        request: Token,
        language: str = Depends(get_language),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
        token_repository: TokenRepository = Depends(get_repository(TokenRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> WrapperResponse:
    strings = strings_factory.get_language(language)

    user_id = get_user_id_from_refresh_token(request.token_access, request.token_refresh, settings.public_key)

    if not user_id:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, strings.WRONG_TOKEN_PAIR)

    user_token = await token_repository.get_token(user_id)
    if request.token_refresh != user_token:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, strings.REFRESH_TOKEN_IS_REVOKED)

    user = await user_repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, strings.USER_DOES_NOT_EXIST_ERROR)

    token_access, token_refresh = create_tokens_for_user(user.id, user.username, settings.private_key)

    await token_repository.update_token(user.id, token_refresh)

    return WrapperResponse(
        payload=UserWithTokenResponse(
            user=user,
            token=Token(token_access=token_access, token_refresh=token_refresh)
        )
    )
