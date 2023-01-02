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

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.database.repositories.phone_repository import PhoneRepository
from app.database.repositories.user_repository import UserRepository
from app.models.domain.user import User, UserInDB
from app.models.schemas.user import UserResponse, UserUpdate, UserChangePhone
from app.models.schemas.wrapper import WrapperResponse
from app.resources import strings

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK, name="users:get-user")
async def get_user(
        user: User = Depends(get_current_user_authorizer()),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> WrapperResponse:
    user: User = await user_repository.get_user_by_username(user.username)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.USER_DOES_NOT_EXIST_ERROR)

    return WrapperResponse(
        payload=UserResponse(
            user=User(id=user.id, phone=user.phone, username=user.username, is_blocked=user.is_blocked)
        )
    )


@router.patch("", status_code=status.HTTP_200_OK, name="users:update-user")
async def update_user(
        request: UserUpdate,
        user: UserInDB = Depends(get_current_user_authorizer()),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> WrapperResponse:
    if request.username and request.username != user.username:
        if await user_repository.is_exists(request.username):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.USERNAME_TAKEN)

    user: User = await user_repository.update_user_by_user_id(user.id, **request.__dict__)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.USER_DOES_NOT_EXIST_ERROR)

    return WrapperResponse(
        payload=UserResponse(
            user=User(id=user.id, phone=user.phone, username=user.username, is_blocked=user.is_blocked)
        )
    )


@router.post("/change_phone", status_code=status.HTTP_200_OK, name="users:change-phone")
async def change_phone(
        request: UserChangePhone,
        user: UserInDB = Depends(get_current_user_authorizer()),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
        phone_repository: PhoneRepository = Depends(get_repository(PhoneRepository)),
) -> WrapperResponse:
    if not await phone_repository.verify_phone_by_code_and_token(
            request.phone, request.verification_code, request.phone_token,
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.VERIFICATION_CODE_IS_WRONG)

    if request.phone == user.phone:
        return WrapperResponse(
            payload=UserResponse(
                user=User(id=user.id, phone=user.phone, username=user.username, is_blocked=user.is_blocked)
            )
        )

    if await phone_repository.is_attached_by_phone(request.phone):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=strings.PHONE_NUMBER_TAKEN)

    user: User = await user_repository.change_user_phone_by_user_id(user.id, **request.__dict__)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.USER_DOES_NOT_EXIST_ERROR)

    return WrapperResponse(
        payload=UserResponse(
            user=User(id=user.id, phone=user.phone, username=user.username, is_blocked=user.is_blocked)
        )
    )
