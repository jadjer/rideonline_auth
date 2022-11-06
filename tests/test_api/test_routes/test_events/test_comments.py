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

from fastapi import (
    FastAPI,
    status,
)
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories import UsersRepository
from app.database.repositories.comments import CommentsRepository
from app.models.domain.event import Event
from app.models.domain.post import Post
from app.models.schemas.comment import (
    CommentInResponse,
    ListOfCommentsInResponse,
)


@pytest.mark.asyncio
async def test_user_can_add_comment(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_event: Event
) -> None:
    created_comment_response = await authorized_client.post(
        initialized_app.url_path_for("comments:create-comment-for-event", event_id=str(test_event.id)),
        json={"comment": {"body": "comment"}},
    )

    created_comment = CommentInResponse(**created_comment_response.json())

    comments_for_post_response = await authorized_client.get(
        initialized_app.url_path_for("comments:get-comments-for-event", event_id=str(test_event.id))
    )

    comments_list = ListOfCommentsInResponse(**comments_for_post_response.json())

    assert len(comments_list.comments) == 1
    assert created_comment.comment == comments_list.comments[0]


@pytest.mark.asyncio
async def test_user_can_delete_own_comment(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_post: Post
) -> None:
    created_comment_response = await authorized_client.post(
        initialized_app.url_path_for("comments:create-comment-for-post", post_id=str(test_post.id)),
        json={"comment": {"body": "comment"}},
    )

    created_comment = CommentInResponse(**created_comment_response.json())

    await authorized_client.delete(
        initialized_app.url_path_for(
            "comments:delete-comment-from-post",
            post_id=str(test_post.id),
            comment_id=str(created_comment.comment.id))
    )

    comments_for_post_response = await authorized_client.get(
        initialized_app.url_path_for(
            "comments:get-comments-for-post",
            post_id=str(test_post.id)
        )
    )

    comments = ListOfCommentsInResponse(**comments_for_post_response.json())

    assert len(comments.comments) == 0


@pytest.mark.asyncio
async def test_user_can_not_delete_not_authored_comment(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_post: Post, session: AsyncSession
) -> None:
    users_repo = UsersRepository(session)
    user = await users_repo.create_user(
        username="test_author",
        phone="+375987654321",
        password="password",
    )

    comments_repo = CommentsRepository(session)
    comment = await comments_repo.create_comment_by_post_id_and_user(test_post.id, user, body="tmp")

    forbidden_response = await authorized_client.delete(
        initialized_app.url_path_for(
            "comments:delete-comment-from-post",
            post_id=str(test_post.id),
            comment_id=str(comment.id),
        )
    )

    assert forbidden_response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_user_will_receive_error_for_not_existing_comment(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_post: Post
) -> None:
    not_found_response = await authorized_client.delete(
        initialized_app.url_path_for(
            "comments:delete-comment-from-post",
            post_id=str(test_post.id),
            comment_id="1",
        )
    )

    assert not_found_response.status_code == status.HTTP_404_NOT_FOUND
