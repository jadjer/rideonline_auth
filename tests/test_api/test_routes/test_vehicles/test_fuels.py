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

from app.models.domain.location import Location
from app.models.domain.vehicle import Vehicle


@pytest.mark.asyncio
async def test_user_can_create_fuel_for_own_vehicle(
        initialized_app: FastAPI,
        authorized_client: AsyncClient,
        test_vehicle: Vehicle,
        test_location: Location
) -> None:
    fuel_data = {
        "location": {
            "id": test_location.id,
            "description": test_location.description,
            "latitude": test_location.latitude,
            "longitude": test_location.longitude
        },
        "quantity": 25,
        "price": 1.23,
        "mileage": test_vehicle.mileage + 500,
        "fuel_type": "petrol_95",
        "is_full": True
    }

    response = await authorized_client.post(
        initialized_app.url_path_for("fuels:create-fuel", vehicle_id=str(test_vehicle.id)),
        json={"fuel": fuel_data}
    )

    assert response.status_code == status.HTTP_200_OK
