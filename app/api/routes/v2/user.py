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
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.responses import JSONResponse

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.get_from_path import get_user_id_from_path, get_language_from_path
from app.database.repositories.phone_repository import PhoneRepository
from app.database.repositories.user_repository import UserRepository
from app.models.domain.user import User, UserInDB
from app.models.schemas.user import UserResponse, UserUpdate, UserChangePhone
from app.models.schemas.wrapper import WrapperResponse
from app.resources import strings

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK, name="users:get-current-user")
async def get_current_user(
        language: str = Depends(get_language_from_path),
        user: User = Depends(get_current_user_authorizer()),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> JSONResponse:
    user: User = await user_repository.get_user_by_username(user.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.USER_DOES_NOT_EXIST_ERROR,
            headers={"Content-Language": language},
        )

    return JSONResponse(
        content=WrapperResponse(
            payload=UserResponse(
                user=User(**user.__dict__),
            )
        ),
        headers={"Content-Language": language},
    )


@router.patch("", status_code=status.HTTP_200_OK, name="users:update-current-user")
async def update_current_user(
        request: UserUpdate,
        language: str = Depends(get_language_from_path),
        user: UserInDB = Depends(get_current_user_authorizer()),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> JSONResponse:
    if request.username and request.username != user.username:
        if await user_repository.is_exists(request.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=strings.USERNAME_TAKEN,
                headers={"Content-Language": language},
            )

    user: User = await user_repository.update_user_by_user_id(user.id, **request.__dict__)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.USER_DOES_NOT_EXIST_ERROR,
            headers={"Content-Language": language},
        )

    return JSONResponse(
        content=WrapperResponse(
            payload=UserResponse(
                user=User(**user.__dict__),
            )
        ),
        headers={"Content-Language": language},
    )


@router.post("/change_phone", status_code=status.HTTP_200_OK, name="users:change-phone-for-current-user")
async def change_phone_for_current_user(
        request: UserChangePhone,
        language: str = Depends(get_language_from_path),
        user: UserInDB = Depends(get_current_user_authorizer()),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
        phone_repository: PhoneRepository = Depends(get_repository(PhoneRepository)),
) -> JSONResponse:
    if not await phone_repository.verify_phone_by_code_and_token(
            request.phone, request.verification_code, request.phone_token,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=strings.VERIFICATION_CODE_IS_WRONG,
            headers={"Content-Language": language},
        )

    if request.phone == user.phone:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=strings.PHONE_NUMBER_TAKEN,
            headers={"Content-Language": language},
        )

    if await phone_repository.is_attached_by_phone(request.phone):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=strings.PHONE_NUMBER_TAKEN,
            headers={"Content-Language": language},
        )

    user: User = await user_repository.change_user_phone_by_user_id(user.id, phone=request.phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.USER_DOES_NOT_EXIST_ERROR,
            headers={"Content-Language": language},
        )

    return JSONResponse(
        content=WrapperResponse(
            payload=UserResponse(
                user=User(**user.__dict__),
            )
        ),
        headers={"Content-Language": language},
    )


@router.get("/{user_id}", status_code=status.HTTP_200_OK, name="users:get-user-by-id")
async def get_user_by_id(
        user_id: int = Depends(get_user_id_from_path),
        language: str = Depends(get_language_from_path),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
) -> JSONResponse:
    user = await user_repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.USER_DOES_NOT_EXIST_ERROR,
            headers={"Content-Language": language},
        )

    return JSONResponse(
        content=WrapperResponse(
            payload=UserResponse(
                user=User(**user.__dict__),
            )
        ),
        headers={"Content-Language": language},
    )
