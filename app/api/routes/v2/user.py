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

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.get_from_path import get_user_id
from app.api.dependencies.get_from_header import get_language
from app.core.config import get_app_settings
from app.core.settings.app import AppSettings
from app.database.repositories.phone_repository import PhoneRepository
from app.database.repositories.user_repository import UserRepository
from app.models.domain.user import User, UserInDB
from app.models.domain.verification_code import VerificationCode
from app.models.schemas.user import UserResponse, UserUpdate, UserChangePhone
from app.models.schemas.wrapper import WrapperResponse
from app.resources import strings_factory
from app.services.verification_code import check_verification_code

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK, name="users:get-current-user")
async def get_current_user(
        language: str = Depends(get_language),
        user: User = Depends(get_current_user_authorizer()),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> WrapperResponse:
    strings = strings_factory.get_language(language)

    user: User = await user_repository.get_user_by_username(user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.USER_DOES_NOT_EXIST_ERROR)

    return WrapperResponse(
        payload=UserResponse(
            user=User(**user.__dict__),
        )
    )


@router.patch("", status_code=status.HTTP_200_OK, name="users:update-current-user")
async def update_current_user(
        request: UserUpdate,
        language: str = Depends(get_language),
        user: UserInDB = Depends(get_current_user_authorizer()),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> WrapperResponse:
    strings = strings_factory.get_language(language)

    if request.username and request.username != user.username:
        if await user_repository.is_exists(request.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.USERNAME_TAKEN)

    user: User = await user_repository.update_user_by_user_id(user.id, **request.__dict__)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.USER_DOES_NOT_EXIST_ERROR)

    return WrapperResponse(
        payload=UserResponse(
            user=User(**user.__dict__),
        )
    )


@router.post("/change_phone", status_code=status.HTTP_200_OK, name="users:change-phone-for-current-user")
async def change_phone_for_current_user(
        request: UserChangePhone,
        language: str = Depends(get_language),
        user: UserInDB = Depends(get_current_user_authorizer()),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
        phone_repository: PhoneRepository = Depends(get_repository(PhoneRepository)),
        settings: AppSettings = Depends(get_app_settings),
) -> WrapperResponse:
    strings = strings_factory.get_language(language)

    verification_code: VerificationCode = await phone_repository.get_verification_code_by_phone(request.phone)
    if not verification_code:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, strings.VERIFICATION_CODE_IS_WRONG)

    if not check_verification_code(verification_code.secret, request.verification_token, request.verification_code, settings.verification_code_timeout):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, strings.VERIFICATION_CODE_IS_WRONG)

    if request.phone == user.phone:
        raise HTTPException(status.HTTP_409_CONFLICT, strings.PHONE_NUMBER_TAKEN)

    if await phone_repository.is_attached_by_phone(request.phone):
        raise HTTPException(status.HTTP_409_CONFLICT, strings.PHONE_NUMBER_TAKEN)

    user: User = await user_repository.change_user_phone_by_user_id(user.id, phone=request.phone)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, strings.USER_DOES_NOT_EXIST_ERROR)

    return WrapperResponse(
        payload=UserResponse(
            user=User(**user.__dict__),
        )
    )


@router.get("/{user_id}", status_code=status.HTTP_200_OK, name="users:get-user-by-id")
async def get_user_by_id(
        user_id: int = Depends(get_user_id),
        language: str = Depends(get_language),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> WrapperResponse:
    strings = strings_factory.get_language(language)

    user = await user_repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, strings.USER_DOES_NOT_EXIST_ERROR)

    return WrapperResponse(
        payload=UserResponse(
            user=User(**user.__dict__),
        )
    )
