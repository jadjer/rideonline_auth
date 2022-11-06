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
    Depends,
    status,
)

from app.api.dependencies.authentication import get_current_user_id_authorizer, get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.events import (
    get_event_confirmation_from_query, get_event_by_id_from_path,
)
from app.api.dependencies.get_id_from_path import get_event_id_from_path
from app.database.errors import EntityDoesNotExists
from app.database.repositories.events_confirmations import EventConfirmationsRepository
from app.models.domain.event import Event
from app.models.domain.event_confirmation import (
    EventConfirmationType,
    EventConfirmation,
)
from app.models.domain.user import User
from app.models.schemas.event_confirmation import EventConfirmationInResponse

router = APIRouter()


@router.post(
    "",
    response_model=EventConfirmationInResponse,
    name="events:confirmation",
    status_code=status.HTTP_200_OK,
)
async def create_confirmation(
        event: Event = Depends(get_event_by_id_from_path),
        event_confirmation: EventConfirmationType = Depends(get_event_confirmation_from_query),
        user: User = Depends(get_current_user_authorizer()),
        confirmation_repo: EventConfirmationsRepository = Depends(get_repository(EventConfirmationsRepository)),
) -> EventConfirmationInResponse:
    confirm: EventConfirmation

    try:
        await confirmation_repo.get_confirmation_by_event_id_and_user_id(event.id, user.id)
        confirm = await confirmation_repo.update_confirmation_by_event_id_and_user_id(
            event.id, user.id, event_confirmation
        )

    except EntityDoesNotExists:
        confirm = await confirmation_repo.create_confirmation_by_event_id_for_user(
            event.id, user.id, event_confirmation
        )

    return EventConfirmationInResponse(
        confirmation=confirm
    )


@router.get(
    "/confirmations",
    response_model=EventConfirmationInResponse,
    name="events:get-confirmations",
    status_code=status.HTTP_200_OK,
)
async def get_confirmations(
        event: Event = Depends(get_event_by_id_from_path),
        event_confirmation: EventConfirmationType = Depends(get_event_confirmation_from_query),
        user: User = Depends(get_current_user_authorizer()),
        confirmation_repo: EventConfirmationsRepository = Depends(get_repository(EventConfirmationsRepository)),
) -> EventConfirmationInResponse:
    confirm: EventConfirmation

    try:
        await confirmation_repo.get_confirmation_by_event_id_and_user_id(event.id, user.id)
        confirm = await confirmation_repo.update_confirmation_by_event_id_and_user_id(
            event.id, user.id, event_confirmation
        )

    except EntityDoesNotExists:
        confirm = await confirmation_repo.create_confirmation_by_event_id_for_user(
            event.id, user.id, event_confirmation
        )

    return EventConfirmationInResponse(
        confirmation=confirm
    )

