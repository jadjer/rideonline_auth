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
    Body,
    status,
    HTTPException
)

from app.api.dependencies.database import get_repository
from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.fuels import get_fuel_by_id_from_path
from app.api.dependencies.vehicle import get_vehicle_by_id_from_path
from app.database.errors import (
    EntityCreateError,
    EntityUpdateError,
    EntityDeleteError,
)
from app.database.repositories.fuels import FuelsRepository
from app.database.repositories.vehicles import VehiclesRepository
from app.models.domain.fuel import Fuel
from app.models.domain.user import User
from app.models.domain.vehicle import Vehicle
from app.models.schemas.fuel import (
    FuelInResponse,
    ListOfFuelsInResponse,
    FuelInCreate,
    FuelInUpdate,
)
from app.resources import strings
from app.services.vehicles import update_vehicle_mileage

router = APIRouter()


@router.post(
    "",
    response_model=FuelInResponse,
    name="fuels:create-fuel",
)
async def create_fuel(
        fuel_create: FuelInCreate = Body(..., embed=True, alias="fuel"),
        user: User = Depends(get_current_user_authorizer()),
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
        fuels_repo: FuelsRepository = Depends(get_repository(FuelsRepository)),
) -> FuelInResponse:
    vehicle_mileage_reduce = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.VEHICLE_MILEAGE_REDUCE
    )
    fuel_create_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.FUEL_CREATE_ERROR
    )

    if fuel_create.mileage and fuel_create.mileage < vehicle.mileage:
        raise vehicle_mileage_reduce

    try:
        fuel = await fuels_repo.create_fuel_by_vehicle_id(vehicle.id, **fuel_create.__dict__)
    except EntityCreateError as exception:
        raise fuel_create_error from exception

    await update_vehicle_mileage(vehicles_repo, vehicle.id, user.id, fuel_create.mileage)

    return FuelInResponse(fuel=fuel)


@router.get(
    "",
    response_model=ListOfFuelsInResponse,
    name="fuels:get-all-fuels"
)
async def get_fuels(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        fuels_repo: FuelsRepository = Depends(get_repository(FuelsRepository)),
) -> ListOfFuelsInResponse:
    fuels = await fuels_repo.get_fuels_by_vehicle_id(vehicle.id)
    return ListOfFuelsInResponse(fuels=fuels, count=len(fuels))


@router.get(
    "/{fuel_id}",
    response_model=FuelInResponse,
    name="fuels:get-fuel"
)
async def get_fuel_by_id(
        fuel: Fuel = Depends(get_fuel_by_id_from_path),
) -> FuelInResponse:
    return FuelInResponse(fuel=fuel)


@router.put(
    "/{fuel_id}",
    response_model=FuelInResponse,
    name="fuels:update-fuel"
)
async def update_reminder_by_id(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        fuel: Fuel = Depends(get_fuel_by_id_from_path),
        fuel_update: FuelInUpdate = Body(..., embed=True, alias="fuel"),
        user: User = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
        fuels_repo: FuelsRepository = Depends(get_repository(FuelsRepository)),
) -> FuelInResponse:
    vehicle_mileage_reduce = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.VEHICLE_MILEAGE_REDUCE
    )
    fuel_update_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.FUEL_UPDATE_ERROR
    )

    if fuel_update.mileage and fuel_update.mileage < vehicle.mileage:
        raise vehicle_mileage_reduce

    try:
        fuel = await fuels_repo.update_fuel_by_id_and_vehicle_id(fuel.id, vehicle.id, **fuel_update.__dict__)
    except EntityUpdateError as exception:
        raise fuel_update_error from exception

    if fuel_update.mileage:
        await update_vehicle_mileage(vehicles_repo, vehicle.id, user.id, fuel_update.mileage)

    return FuelInResponse(fuel=fuel)


@router.delete(
    "/{fuel_id}",
    name="fuels:delete-fuel",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_fuel_by_id(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        fuel: Fuel = Depends(get_fuel_by_id_from_path),
        fuels_repo: FuelsRepository = Depends(get_repository(FuelsRepository)),
) -> None:
    fuel_delete_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.FUEL_DELETE_ERROR
    )

    try:
        await fuels_repo.delete_fuel_by_id_and_vehicle_id(fuel.id, vehicle.id)
    except EntityDeleteError as exception:
        raise fuel_delete_error from exception
