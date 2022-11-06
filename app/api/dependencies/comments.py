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

from fastapi import Depends, HTTPException, Path, status

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.database.errors import EntityDoesNotExists
from app.database.repositories.comments import CommentsRepository
from app.models.domain.comment import Comment
from app.models.domain.user import User
from app.resources import strings
from app.services.comments import check_user_can_modify_comment


async def get_comment_by_id_from_path(
        comment_id: int = Path(..., ge=1),
        comments_repo: CommentsRepository = Depends(get_repository(CommentsRepository)),
) -> Comment:
    comment_not_found = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.COMMENT_DOES_NOT_EXIST)

    try:
        return await comments_repo.get_comment_by_id(comment_id)
    except EntityDoesNotExists as exception:
        raise comment_not_found from exception


def check_comment_modification_permissions(
        comment: Comment = Depends(get_comment_by_id_from_path),
        user: User = Depends(get_current_user_authorizer()),
) -> None:
    if not check_user_can_modify_comment(user, comment):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.USER_IS_NOT_AUTHOR_OF_POST,
        )
