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

from datetime import datetime
from fastapi import FastAPI, status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.errors import EntityDoesNotExists
from app.database.repositories import UsersRepository
from app.database.repositories.events import EventsRepository
from app.models.domain.event import Event
from app.models.domain.location import Location
from app.models.domain.post import Post
from app.models.domain.user import User
from app.models.schemas.events import (
    EventInResponse,
    ListOfEventsInResponse,
)


@pytest.mark.asyncio
async def test_user_can_not_create_event_with_duplicated_title(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_event: Event
) -> None:
    event_data = {
        "title": "Test event",
        "description": "¯\\_(ツ)_/¯",
        "thumbnail": "",
        "body": "does not matter",
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "location": {
            "description": "Test location",
            "latitude": 1.23,
            "longitude": 4.56
        }
    }
    response = await authorized_client.post(
        initialized_app.url_path_for("events:create-event"), json={"event": event_data}
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert "errors" in response.json()


@pytest.mark.asyncio
async def test_user_can_create_event(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_user: User
) -> None:
    event_data = {
        "title": "Test event",
        "description": "¯\\_(ツ)_/¯",
        "thumbnail": "",
        "body": "does not matter",
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "location": {
            "description": "Test location",
            "latitude": 1.23,
            "longitude": 4.56
        }
    }
    response = await authorized_client.post(
        initialized_app.url_path_for("events:create-event"), json={"event": event_data}
    )

    event = EventInResponse(**response.json())

    assert event.event.title == event_data["title"]
    assert event.event.author.username == test_user.username


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "api_method, route_name",
    (("GET", "events:get-event"), ("PUT", "events:update-event")),
)
async def test_user_can_not_retrieve_not_existing_event(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        test_event: Event,
        api_method: str,
        route_name: str,
) -> None:
    response = await authorized_client.request(
        api_method, initialized_app.url_path_for(route_name, event_id=str(test_event.id + 1))
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_user_can_retrieve_event_if_exists(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_event: Event,
) -> None:
    response = await authorized_client.get(
        initialized_app.url_path_for("events:get-event", event_id=str(test_event.id))
    )

    event = EventInResponse(**response.json())

    assert response.status_code == status.HTTP_200_OK
    assert event.event == test_event


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
async def test_user_can_update_event(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        test_event: Event,
        update_field: str,
        update_value: str
) -> None:
    response = await authorized_client.put(
        initialized_app.url_path_for("events:update-event", event_id=str(test_event.id)),
        json={"event": {update_field: update_value}},
    )

    assert response.status_code == status.HTTP_200_OK

    event = EventInResponse(**response.json()).event
    event_as_dict = event.dict()

    assert event_as_dict[update_field] == update_value


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "api_method, route_name",
    (("PUT", "events:update-event"), ("DELETE", "events:delete-event")),
)
async def test_user_can_not_modify_event_that_is_not_authored_by_him(
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

    events_repo = EventsRepository(session)
    event = await events_repo.create_event_by_user_id(
        user.id,
        title="Test Slug",
        description="Slug for tests",
        thumbnail="",
        body="Test " * 100,
        started_at=datetime.now(),
        location=Location(
            description="Test location",
            latitude=1.23,
            longitude=4.56
        )
    )

    response = await authorized_client.request(
        api_method,
        initialized_app.url_path_for(route_name, event_id=str(event.id)),
        json={"event": {"title": "Updated Title"}},
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.asyncio
async def test_user_can_delete_his_event(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        test_event: Event,
        session: AsyncSession,
) -> None:
    response = await authorized_client.delete(
        initialized_app.url_path_for("events:delete-event", event_id=str(test_event.id))
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT

    events_repo = EventsRepository(session)
    with pytest.raises(EntityDoesNotExists):
        await events_repo.get_event_by_id(test_event.id)


@pytest.mark.asyncio
async def test_user_receiving_feed_with_limit_and_offset(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        test_post: Post,
        test_event: Event,
        session: AsyncSession,
) -> None:
    users_repo = UsersRepository(session)
    events_repo = EventsRepository(session)

    for i in range(5):
        user = await users_repo.create_user(
            username=f"user_{i}", phone=f"+3751234567{i}", password="password"
        )

        for j in range(5):
            await events_repo.create_event_by_user_id(
                user.id,
                title=f"Post {i}{j}",
                description="tmp",
                thumbnail="",
                body="tmp",
                started_at=datetime.now(),
                location=Location(
                    description="Test location",
                    latitude=1.23,
                    longitude=4.56
                )
            )

    full_response = await authorized_client.get(
        initialized_app.url_path_for("events:get-events")
    )
    full_events = ListOfEventsInResponse(**full_response.json())

    response = await authorized_client.get(
        initialized_app.url_path_for("events:get-events"),
        params={"limit": 2, "offset": 3},
    )
    events_from_response = ListOfEventsInResponse(**response.json())

    assert full_events.events[3:5] == events_from_response.events


@pytest.mark.asyncio
async def test_filtering_with_limit_and_offset(
        initialized_app: FastAPI, authorized_client: AsyncClient, test_user: User, session: AsyncSession,
) -> None:
    events_repo = EventsRepository(session)

    for i in range(5, 10):
        await events_repo.create_event_by_user_id(
            test_user.id,
            title=f"Event {i}",
            description="tmp",
            thumbnail="",
            body="tmp",
            started_at=datetime.now(),
            location=Location(
                description="Test location",
                latitude=1.23,
                longitude=4.56
            )
        )

    full_response = await authorized_client.get(
        initialized_app.url_path_for("events:get-events")
    )
    full_events = ListOfEventsInResponse(**full_response.json())

    response = await authorized_client.get(
        initialized_app.url_path_for("events:get-events"), params={"limit": 2, "offset": 3}
    )

    events_from_response = ListOfEventsInResponse(**response.json())

    assert full_events.events[3:5] == events_from_response.events
