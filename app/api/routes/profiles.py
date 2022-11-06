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

from fastapi import (
    APIRouter,
    Body,
    Depends,
    HTTPException,
    status,
    Query,
)

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.get_id_from_path import get_user_id_from_path
from app.database.errors import EntityDoesNotExists, EntityUpdateError
from app.database.repositories.profiles import ProfilesRepository
from app.models.schemas.profile import (
    ProfileInUpdate,
    ProfileInResponse,
    ListOfProfileInResponse, ProfilesFilter,
)
from app.resources import strings

router = APIRouter()


@router.get(
    "/me",
    response_model=ProfileInResponse,
    name="profiles:get-my-profile"
)
async def get_my_profile(
        user_id: int = Depends(get_current_user_authorizer()),
        profiles_repo: ProfilesRepository = Depends(get_repository(ProfilesRepository)),
) -> ProfileInResponse:
    profile_not_found = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.PROFILE_DOES_NOT_EXISTS)

    try:
        profile = await profiles_repo.get_profile_by_user_id(user_id)
    except EntityDoesNotExists as exception:
        raise profile_not_found from exception

    return ProfileInResponse(profile=profile)


@router.get(
    "/{user_id}",
    response_model=ProfileInResponse,
    name="profiles:get-profile",
    dependencies=[
        Depends(get_current_user_authorizer())
    ]
)
async def get_profile_by_id(
        user_id: int = Depends(get_user_id_from_path),
        profiles_repo: ProfilesRepository = Depends(get_repository(ProfilesRepository)),
) -> ProfileInResponse:
    request_error = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.PROFILE_DOES_NOT_EXISTS)

    try:
        profile = await profiles_repo.get_profile_by_user_id(user_id)
    except EntityDoesNotExists as existence_error:
        raise request_error from existence_error

    return ProfileInResponse(profile=profile)


@router.put(
    "/me",
    response_model=ProfileInResponse,
    name="profiles:update-my-profile"
)
async def update_my_profile(
        profile_update: ProfileInUpdate = Body(..., embed=True, alias="user"),
        user_id: int = Depends(get_current_user_authorizer()),
        profiles_repo: ProfilesRepository = Depends(get_repository(ProfilesRepository)),
) -> ProfileInResponse:
    update_error = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=strings.USERNAME_TAKEN)

    try:
        profile = await profiles_repo.update_profile(user_id, **profile_update.__dict__)
    except EntityUpdateError as exception:
        raise update_error from exception

    return ProfileInResponse(profile=profile)
