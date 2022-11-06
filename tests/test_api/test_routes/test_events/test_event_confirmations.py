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
    status
)
from httpx import AsyncClient

from app.models.domain.event import Event


@pytest.mark.asyncio
async def test_user_can_confirmation_planned_event(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_event: Event
) -> None:
    response = await authorized_client.post(
        initialized_app.url_path_for("events:confirmation", event_id=str(test_event.id)),
        params={"confirmation": "yes"}
    )

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.asyncio
async def test_user_can_confirmation_not_existing_event(
        initialized_app: FastAPI, authorized_client: AsyncClient
) -> None:
    response = await authorized_client.post(
        initialized_app.url_path_for("events:confirmation", event_id=str(1)),
        params={"confirmation": "yes"}
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_user_can_not_confirmation_planned_event_that_is_not_authored_by_him(
        initialized_app: FastAPI, client: AsyncClient, test_event: Event
) -> None:
    response = await client.post(
        initialized_app.url_path_for("events:confirmation", event_id=str(test_event.id)),
        params={"confirmation": "yes"}
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
