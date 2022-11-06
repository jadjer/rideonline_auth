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

from typing import Optional

from fastapi import Depends, HTTPException, Query
from fastapi import status

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.get_id_from_path import get_post_id_from_path
from app.database.errors import EntityDoesNotExists
from app.database.repositories.posts import PostsRepository
from app.models.domain.post import Post
from app.models.domain.profile import Profile
from app.models.domain.user import User
from app.models.schemas.post import (
    DEFAULT_ARTICLES_LIMIT,
    DEFAULT_ARTICLES_OFFSET,
    PostsFilter,
)
from app.resources import strings
from app.services.posts import check_user_can_modify_post


def get_posts_filter(
        limit: int = Query(DEFAULT_ARTICLES_LIMIT, ge=1),
        offset: int = Query(DEFAULT_ARTICLES_OFFSET, ge=0),
) -> PostsFilter:
    return PostsFilter(
        limit=limit,
        offset=offset,
    )


async def get_post_by_id_from_path(
        post_id: int = Depends(get_post_id_from_path),
        posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
) -> Post:
    try:
        return await posts_repo.get_post_by_id(post_id)
    except EntityDoesNotExists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.POST_DOES_NOT_EXISTS,
        )


def check_post_modification_permissions(
        current_post: Post = Depends(get_post_by_id_from_path),
        user: User = Depends(get_current_user_authorizer()),
) -> None:
    if not check_user_can_modify_post(user, current_post):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.USER_IS_NOT_AUTHOR_OF_POST,
        )
