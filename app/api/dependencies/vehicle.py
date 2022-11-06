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
    Depends,
    HTTPException,
    status,
    Path,
)

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.database.errors import EntityDoesNotExists
from app.database.repositories.vehicles import VehiclesRepository
from app.models.domain.user import User
from app.models.domain.vehicle import Vehicle
from app.resources import strings


def get_vehicle_id_from_path(vehicle_id: int = Path(..., ge=1)) -> int:
    return vehicle_id


async def get_vehicle_by_id_from_path(
        vehicle_id: int = Depends(get_vehicle_id_from_path),
        user: User = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> Vehicle:
    vehicle_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.VEHICLE_DOES_NOT_EXIST_ERROR
    )

    try:
        vehicle = await vehicles_repo.get_vehicle_by_id_and_user_id(vehicle_id, user.id)
    except EntityDoesNotExists as exception:
        raise vehicle_not_found from exception

    return vehicle
