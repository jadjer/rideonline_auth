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


# @pytest.mark.asyncio
# async def test_user_can_add_comment(
#         initialized_app: FastAPI, authorized_client: AsyncClient
# ) -> None:
#     created_comment = CommentInResponse(**created_comment_response.json())
#
#     comments_for_post_response = await authorized_client.get(
#         initialized_app.url_path_for("comments:get-comments-for-post", post_id=str(test_post.id))
#     )
#
#     comments_list = ListOfCommentsInResponse(**comments_for_post_response.json())
#
#     assert len(comments_list.comments) == 1
#     assert created_comment.comment == comments_list.comments[0]
