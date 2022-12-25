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
    PhoneToken, Phone,
)
from app.models.schemas.user import (
    UserCreate,
    UserLogin,
    UserWithTokenResponse,
    Token, Username,
)
from app.models.schemas.wrapper import WrapperResponse
from app.services.token import create_tokens_for_user
from app.services.validate import check_phone_is_valid
from app.services.sms import send_verify_code_to_phone
from app.api.dependencies.database import get_repository
from app.resources import strings

router = APIRouter()


@router.post("/useranme", status_code=status.HTTP_200_OK, name="exist:username")
async def exist_username(
        request: Username,
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> WrapperResponse:
    if not await user_repository.is_exists(request.username):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.USERNAME_DOES_NOT_EXIST)

    return WrapperResponse()


@router.post("/phone", status_code=status.HTTP_200_OK, name="exist:phone")
async def exist_phone(
        request: Phone,
        phone_repository: PhoneRepository = Depends(get_repository(PhoneRepository)),
) -> WrapperResponse:
    if not await phone_repository.is_attached_by_phone(request.phone):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.PHONE_NUMBER_DOES_NOT_EXIST)

    return WrapperResponse()
