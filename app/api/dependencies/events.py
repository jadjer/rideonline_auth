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

from fastapi import (
    Query,
    Depends,
    HTTPException,
    status,
)

from app.api.dependencies.authentication import get_current_user_id_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.get_id_from_path import get_event_id_from_path
from app.database.errors import EntityDoesNotExists
from app.database.repositories.events import EventsRepository
from app.models.domain.event import EventState, Event
from app.models.domain.event_confirmation import EventConfirmationType
from app.models.schemas.events import (
    DEFAULT_ARTICLES_LIMIT,
    DEFAULT_ARTICLES_OFFSET,
    EventsFilter,
)
from app.resources import strings
from app.services.events import check_user_can_modify_event


def get_events_filters(
        state: EventState = EventState.PLANNED,
        limit: int = Query(DEFAULT_ARTICLES_LIMIT, ge=1),
        offset: int = Query(DEFAULT_ARTICLES_OFFSET, ge=0),
) -> EventsFilter:
    return EventsFilter(state=state, limit=limit, offset=offset)


async def get_event_by_id_from_path(
        event_id: int = Depends(get_event_id_from_path),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
) -> Event:
    try:
        return await events_repo.get_event_by_id(event_id)
    except EntityDoesNotExists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=strings.EVENT_DOES_NOT_EXIST_ERROR,
        )


def get_event_confirmation_from_query(
        confirmation: EventConfirmationType = Query(...),
) -> EventConfirmationType:
    return confirmation


def check_event_permissions(
        event: Event = Depends(get_event_by_id_from_path),
        user_id: int = Depends(get_current_user_id_authorizer()),
) -> None:
    if not check_user_can_modify_event(user_id, event):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=strings.USER_IS_NOT_AUTHOR_OF_EVENT,
        )
