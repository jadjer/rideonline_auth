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

from fastapi import APIRouter, Depends, Body, HTTPException, status

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.get_from_path import get_user_id_from_path
from app.database import UserRepository
from app.database.repositories.profile_repository import ProfileRepository
from app.models.domain.user import User
from app.models.schemas.profile import ProfileResponse, ProfileUpdate
from app.resources import strings

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK, name="profiles:get-my-profile")
async def get_my_profile(
        user: User = Depends(get_current_user_authorizer()),
        profile_repository: ProfileRepository = Depends(get_repository(ProfileRepository)),
) -> ProfileResponse:
    profile = await profile_repository.get_profile_by_id(user.id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.PROFILE_DOES_NOT_EXISTS)

    return ProfileResponse(
        user=User(id=user.id, phone=user.phone, username=user.username, is_blocked=user.is_blocked),
        profile=profile
    )


@router.get("/{user_id}", status_code=status.HTTP_200_OK, name="profiles:get-profile-by-id")
async def get_profile_by_id(
        user_id: int = Depends(get_user_id_from_path),
        user_repository: UserRepository = Depends(get_repository(UserRepository)),
        profile_repository: ProfileRepository = Depends(get_repository(ProfileRepository)),
) -> ProfileResponse:
    user = await user_repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.USER_DOES_NOT_EXIST_ERROR)

    profile = await profile_repository.get_profile_by_id(user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.PROFILE_DOES_NOT_EXISTS)

    return ProfileResponse(
        user=User(id=user.id, phone=user.phone, username=user.username, is_blocked=user.is_blocked),
        profile=profile
    )


@router.patch("", status_code=status.HTTP_200_OK, name="profiles:update-profile")
async def update_profile(
        request: ProfileUpdate = Body(..., alias="profile"),
        user: User = Depends(get_current_user_authorizer()),
        profile_repository: ProfileRepository = Depends(get_repository(ProfileRepository)),
) -> ProfileResponse:
    profile = await profile_repository.update_profile(user.id, **request.profile.__dict__)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.PROFILE_DOES_NOT_EXISTS)

    return ProfileResponse(
        user=User(id=user.id, phone=user.phone, username=user.username, is_blocked=user.is_blocked),
        profile=profile
    )
