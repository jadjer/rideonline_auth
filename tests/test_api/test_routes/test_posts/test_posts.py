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

import pytest

from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.errors import EntityDoesNotExists
from app.database.repositories import UsersRepository
from app.database.repositories.posts import PostsRepository
from app.models.domain.post import Post
from app.models.domain.user import User
from app.models.schemas.post import PostInResponse, ListOfPostsInResponse


@pytest.mark.asyncio
async def test_user_can_not_create_post_with_duplicated_title(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_post: Post
) -> None:
    post_data = {
        "title": "Test post",
        "description": "¯\\_(ツ)_/¯",
        "thumbnail": "",
        "body": "does not matter",
    }
    response = await authorized_client.post(
        initialized_app.url_path_for("posts:create-post"), json={"post": post_data}
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "errors" in response.json()


@pytest.mark.asyncio
async def test_user_can_create_post(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_user: User
) -> None:
    post_data = {
        "title": "Test post",
        "description": "¯\\_(ツ)_/¯",
        "thumbnail": "",
        "body": "does not matter",
    }
    response = await authorized_client.post(
        initialized_app.url_path_for("posts:create-post"), json={"post": post_data}
    )

    post = PostInResponse(**response.json())

    assert post.post.title == post_data["title"]
    assert post.post.author.username == test_user.username


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "api_method, route_name",
    (("GET", "posts:get-post"), ("PUT", "posts:update-post")),
)
async def test_user_can_not_retrieve_not_existing_post(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        test_post: Post,
        api_method: str,
        route_name: str,
) -> None:
    response = await authorized_client.request(
        api_method, initialized_app.url_path_for(route_name, post_id=str(test_post.id + 1))
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_user_can_retrieve_post_if_exists(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_post: Post,
) -> None:
    response = await authorized_client.get(
        initialized_app.url_path_for("posts:get-post", post_id=str(test_post.id))
    )

    post = PostInResponse(**response.json())

    assert post.post == test_post


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_field, update_value",
    (
            ("title", "New Title"),
            ("description", "new description"),
            ("thumbnail", ""),
            ("body", "new body"),
    ),
)
async def test_user_can_update_post(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        test_post: Post,
        update_field: str,
        update_value: str
) -> None:
    response = await authorized_client.put(
        initialized_app.url_path_for("posts:update-post", post_id=str(test_post.id)),
        json={"post": {update_field: update_value}},
    )

    assert response.status_code == status.HTTP_200_OK

    post = PostInResponse(**response.json()).post
    post_as_dict = post.dict()

    assert post_as_dict[update_field] == update_value


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "api_method, route_name",
    (("PUT", "posts:update-post"), ("DELETE", "posts:delete-post")),
)
async def test_user_can_not_modify_post_that_is_not_authored_by_him(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        session: AsyncSession,
        api_method: str,
        route_name: str,
) -> None:
    users_repo = UsersRepository(session)
    user = await users_repo.create_user(
        username="test_author", phone="+375987654321", password="password"
    )

    posts_repo = PostsRepository(session)
    post = await posts_repo.create_post_by_user_id(
        user.id,
        title="Test Slug",
        description="Slug for tests",
        thumbnail="",
        body="Test " * 100,
    )

    response = await authorized_client.request(
        api_method,
        initialized_app.url_path_for(route_name, post_id=str(post.id)),
        json={"post": {"title": "Updated Title"}},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_user_can_delete_his_post(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        test_post: Post,
        session: AsyncSession,
) -> None:
    response = await authorized_client.delete(
        initialized_app.url_path_for("posts:delete-post", post_id=str(test_post.id))
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    posts_repo = PostsRepository(session)
    with pytest.raises(EntityDoesNotExists):
        await posts_repo.get_post_by_id(test_post.id)


@pytest.mark.asyncio
async def test_user_receiving_feed_with_limit_and_offset(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        test_post: Post,
        test_user: User,
        session: AsyncSession,
) -> None:
    users_repo = UsersRepository(session)
    posts_repo = PostsRepository(session)

    for i in range(5):
        user = await users_repo.create_user(
            username=f"user_{i}", phone=f"+3751234567{i}", password="password"
        )

        for j in range(5):
            await posts_repo.create_post_by_user_id(
                user.id,
                title=f"Post {i}{j}",
                description="tmp",
                thumbnail="",
                body="tmp",
            )

    full_response = await authorized_client.get(
        initialized_app.url_path_for("posts:get-posts")
    )
    full_posts = ListOfPostsInResponse(**full_response.json())

    response = await authorized_client.get(
        initialized_app.url_path_for("posts:get-posts"),
        params={"limit": 2, "offset": 3},
    )
    posts_from_response = ListOfPostsInResponse(**response.json())

    assert full_posts.posts[3:5] == posts_from_response.posts


@pytest.mark.asyncio
async def test_filtering_with_limit_and_offset(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_user: User, session: AsyncSession,
) -> None:
    posts_repo = PostsRepository(session)

    for i in range(5, 10):
        await posts_repo.create_post_by_user_id(
            test_user.id,
            title=f"Post {i}",
            description="tmp",
            thumbnail="",
            body="tmp",
        )

    full_response = await authorized_client.get(
        initialized_app.url_path_for("posts:get-posts")
    )
    full_posts = ListOfPostsInResponse(**full_response.json())

    response = await authorized_client.get(
        initialized_app.url_path_for("posts:get-posts"), params={"limit": 2, "offset": 3}
    )

    posts_from_response = ListOfPostsInResponse(**response.json())

    assert full_posts.posts[3:5] == posts_from_response.posts
