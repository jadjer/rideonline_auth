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

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status

from app.api.dependencies.posts import (
    check_post_modification_permissions,
    get_posts_filter,
    get_post_id_from_path,
)
from app.api.dependencies.authentication import get_current_user_authorizer, get_current_user_id_authorizer
from app.api.dependencies.database import get_repository
from app.database.errors import (
    EntityCreateError,
    EntityDoesNotExists, EntityDeleteError,
)
from app.database.repositories.posts import PostsRepository
from app.models.domain.user import User
from app.models.schemas.post import (
    PostInCreate,
    PostInResponse,
    PostInUpdate,
    PostsFilter,
    ListOfPostsInResponse,
)
from app.resources import strings
from app.services.posts import check_post_exist_by_title

router = APIRouter()


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=PostInResponse,
    name="posts:create-post",
)
async def create_post(
        post_create: PostInCreate = Body(..., embed=True, alias="post"),
        user_id: int = Depends(get_current_user_id_authorizer()),
        posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
) -> PostInResponse:
    post_already_exists = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=strings.POST_ALREADY_EXISTS
    )
    post_create_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.POST_CREATE_ERROR
    )

    if await check_post_exist_by_title(posts_repo, post_create.title):
        raise post_already_exists

    try:
        post = await posts_repo.create_post_by_user_id(user_id, **post_create.__dict__)
    except EntityCreateError as exception:
        raise post_create_error from exception

    return PostInResponse(post=post)


@router.get(
    "",
    response_model=ListOfPostsInResponse,
    name="posts:get-posts"
)
async def get_posts_with_filter(
        posts_filter: PostsFilter = Depends(get_posts_filter),
        posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
) -> ListOfPostsInResponse:
    posts = await posts_repo.get_posts_with_filter(
        limit=posts_filter.limit,
        offset=posts_filter.offset,
    )

    return ListOfPostsInResponse(posts=posts, count=len(posts))


@router.get(
    "/{post_id}",
    response_model=PostInResponse,
    name="posts:get-post"
)
async def get_post_by_id(
        post_id: int = Depends(get_post_id_from_path),
        posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
) -> PostInResponse:
    post_not_found = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.POST_DOES_NOT_EXISTS)

    try:
        post = await posts_repo.get_post_by_id(post_id)
    except EntityDoesNotExists as exception:
        raise post_not_found from exception

    return PostInResponse(post=post)


@router.put(
    "/{post_id}",
    response_model=PostInResponse,
    name="posts:update-post",
    dependencies=[Depends(check_post_modification_permissions)],
)
async def update_post_by_id(
        post_id: int = Depends(get_post_id_from_path),
        post_update: PostInUpdate = Body(..., embed=True, alias="post"),
        user_id: int = Depends(get_current_user_id_authorizer()),
        posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
) -> PostInResponse:
    post_already_exists = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=strings.POST_ALREADY_EXISTS
    )
    post_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.POST_DOES_NOT_EXISTS
    )

    if await check_post_exist_by_title(posts_repo, post_update.title):
        raise post_already_exists

    try:
        post = await posts_repo.update_post_by_id_and_user_id(post_id, user_id, **post_update.__dict__)
    except EntityDoesNotExists as exception:
        raise post_not_found from exception

    return PostInResponse(post=post)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="posts:delete-post",
    dependencies=[Depends(check_post_modification_permissions)],
    response_class=Response,
)
async def delete_post_by_id(
        post_id: int = Depends(get_post_id_from_path),
        user_id: int = Depends(get_current_user_id_authorizer()),
        posts_repo: PostsRepository = Depends(get_repository(PostsRepository)),
) -> None:
    post_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.POST_DOES_NOT_EXISTS
    )
    post_delete_error = HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=strings.POST_DELETE_ERROR
    )

    try:
        await posts_repo.delete_post_by_id_and_user_id(post_id, user_id)
    except EntityDoesNotExists as exception:
        raise post_not_found from exception
    except EntityDeleteError as exception:
        raise post_delete_error from exception
