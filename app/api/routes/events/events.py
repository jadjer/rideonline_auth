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
    status,
    Depends,
    Body,
    HTTPException,
)

from app.api.dependencies.authentication import get_current_user_id_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.events import (
    get_events_filters,
    get_event_id_from_path,
    check_event_permissions,
)
from app.database.errors import (
    EntityDoesNotExists,
    EntityAlreadyExists,
    EntityCreateError,
)
from app.database.repositories.events import EventsRepository
from app.models.schemas.events import (
    EventsFilter,
    ListOfEventsInResponse,
    EventInResponse,
    EventInCreate,
    EventInUpdate,
)
from app.resources import strings
from app.services.events import check_event_exist_by_title

router = APIRouter()


@router.post(
    "",
    response_model=EventInResponse,
    name="events:create-event",
    status_code=status.HTTP_201_CREATED,
)
async def create_event(
        event_create: EventInCreate = Body(..., embed=True, alias="event"),
        user_id: int = Depends(get_current_user_id_authorizer()),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
) -> EventInResponse:
    event_already_exists = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=strings.EVENT_ALREADY_EXISTS
    )
    event_create_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.EVENT_CREATE_ERROR
    )

    if await check_event_exist_by_title(events_repo, event_create.title):
        raise event_already_exists

    try:
        event = await events_repo.create_event_by_user_id(user_id, **event_create.__dict__)
    except EntityCreateError as exception:
        raise event_create_error from exception

    return EventInResponse(event=event)


@router.get(
    "",
    response_model=ListOfEventsInResponse,
    name="events:get-events",
)
async def get_events(
        events_filter: EventsFilter = Depends(get_events_filters),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
) -> ListOfEventsInResponse:
    event_not_found = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.EVENT_DOES_NOT_EXIST_ERROR)

    try:
        events = await events_repo.get_events_with_filter(
            state=events_filter.state,
            limit=events_filter.limit,
            offset=events_filter.offset
        )
    except EntityDoesNotExists as exception:
        raise event_not_found from exception

    return ListOfEventsInResponse(events=events, events_count=len(events))


@router.get(
    "/{event_id}",
    response_model=EventInResponse,
    name="events:get-event",
)
async def get_event(
        event_id: int = Depends(get_event_id_from_path),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
) -> EventInResponse:
    event_not_found = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.EVENT_DOES_NOT_EXIST_ERROR)

    try:
        event = await events_repo.get_event_by_id(event_id)
    except EntityDoesNotExists as exception:
        raise event_not_found from exception

    return EventInResponse(event=event)


@router.put(
    "/{event_id}",
    response_model=EventInResponse,
    name="events:update-event",
    dependencies=[
        Depends(check_event_permissions),
    ],
)
async def update_event(
        event_id: int = Depends(get_event_id_from_path),
        event_update: EventInUpdate = Body(..., embed=True, alias="event"),
        user_id: int = Depends(get_current_user_id_authorizer()),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
) -> EventInResponse:
    event_already_exists = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=strings.EVENT_ALREADY_EXISTS
    )
    event_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.EVENT_DOES_NOT_EXIST_ERROR
    )

    if await check_event_exist_by_title(events_repo, event_update.title):
        raise event_already_exists

    try:
        event = await events_repo.update_event_by_id_and_user_id(event_id, user_id, **event_update.__dict__)
    except EntityDoesNotExists as exception:
        raise event_not_found from exception

    return EventInResponse(event=event)


@router.delete(
    "/{event_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="events:delete-event",
    dependencies=[
        Depends(check_event_permissions),
    ],
)
async def delete_event(
        event_id: int = Depends(get_event_id_from_path),
        user_id: int = Depends(get_current_user_id_authorizer()),
        events_repo: EventsRepository = Depends(get_repository(EventsRepository)),
) -> None:
    event_not_found = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=strings.EVENT_DOES_NOT_EXIST_ERROR)

    try:
        await events_repo.delete_event_by_id_and_user_id(event_id, user_id)
    except EntityDoesNotExists as exception:
        raise event_not_found from exception
