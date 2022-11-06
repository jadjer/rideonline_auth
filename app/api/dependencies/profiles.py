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

from fastapi import Depends, HTTPException, Path, status, Query

from app.api.dependencies.database import get_repository
from app.database.errors import EntityDoesNotExists
from app.database.repositories.profiles import ProfilesRepository
from app.models.domain.profile import Profile
from app.models.schemas.post import PostsFilter
from app.models.schemas.profile import (
    DEFAULT_PROFILES_LIMIT,
    DEFAULT_PROFILES_OFFSET,
)
from app.resources import strings


def get_profiles_filter(
        limit: int = Query(DEFAULT_PROFILES_LIMIT, ge=1),
        offset: int = Query(DEFAULT_PROFILES_OFFSET, ge=0),
) -> PostsFilter:
    return PostsFilter(limit=limit, offset=offset)


async def get_profile_by_username_from_path(
        username: str = Path(..., min_length=1),
        profiles_repo: ProfilesRepository = Depends(get_repository(ProfilesRepository)),
) -> Profile:
    try:
        return await profiles_repo.get_profile_by_username(username=username)
    except EntityDoesNotExists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.USER_DOES_NOT_EXIST_ERROR,
        )
