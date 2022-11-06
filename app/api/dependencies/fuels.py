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
    Path,
    Depends,
    HTTPException,
    status,
)

from app.api.dependencies.database import get_repository
from app.api.dependencies.vehicle import get_vehicle_by_id_from_path
from app.database.errors import EntityDoesNotExists
from app.database.repositories.fuels import FuelsRepository
from app.models.domain.fuel import Fuel
from app.models.domain.vehicle import Vehicle
from app.resources import strings


def get_fuel_id_from_path(fuel_id: int = Path(..., ge=1)) -> int:
    return fuel_id


async def get_fuel_by_id_from_path(
        fuel_id: int = Depends(get_fuel_id_from_path),
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        fuels_repo: FuelsRepository = Depends(get_repository(FuelsRepository)),
) -> Fuel:
    fuel_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.FUEL_DOES_NOT_EXIST_ERROR
    )

    try:
        fuel = await fuels_repo.get_fuel_by_id_and_vehicle_id(fuel_id, vehicle.id)
    except EntityDoesNotExists as exception:
        raise fuel_not_found from exception

    return fuel
