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
from app.database.repositories.profile_repository import ProfileRepository
from app.models.domain.user import User
from app.models.schemas.profile import ProfileResponse, ProfileUpdate
from app.resources import strings

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK, name="profile:get")
async def get_profile(
        user: User = Depends(get_current_user_authorizer()),
        profile_repository: ProfileRepository = Depends(get_repository(ProfileRepository)),
) -> ProfileResponse:
    profile = await profile_repository.get_profile(user.username)
    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.PROFILE_DOES_NOT_EXISTS)

    return ProfileResponse(profile=profile)


@router.patch("", status_code=status.HTTP_200_OK, name="profile:update")
async def update_profile(
        profile_update: ProfileUpdate = Body(..., alias="profile"),
        user: User = Depends(get_current_user_authorizer()),
        profile_repository: ProfileRepository = Depends(get_repository(ProfileRepository)),
) -> ProfileResponse:
    profile = await profile_repository.update_profile(user.username, **profile_update.profile.__dict__)
    if not profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.PROFILE_DOES_NOT_EXISTS)

    return ProfileResponse(profile=profile)
