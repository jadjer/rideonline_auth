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

from app.api.dependencies.authentication import get_current_user_authorizer
from app.api.dependencies.database import get_repository
from app.api.dependencies.vehicle import get_vehicle_by_id_from_path
from app.database.errors import (
    EntityDeleteError,
    EntityCreateError,
    EntityUpdateError,
)
from app.database.repositories.vehicles import VehiclesRepository
from app.models.domain.user import User
from app.models.domain.vehicle import Vehicle
from app.models.schemas.vehicle import (
    VehicleInResponse,
    ListOfVehiclesInResponse,
    VehicleInCreate,
    VehicleInUpdate,
)
from app.resources import strings
from app.services.vehicles import (
    check_vin_is_taken,
    check_registration_plate_is_taken,
)

router = APIRouter()


@router.post(
    "",
    response_model=VehicleInResponse,
    name="vehicles:create-vehicle"
)
async def create_vehicle(
        vehicle_create: VehicleInCreate = Body(..., embed=True, alias="vehicle"),
        user: User = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> VehicleInResponse:
    vehicle_vin_exist = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=strings.VEHICLE_CONFLICT_VIN_ERROR
    )
    vehicle_reg_plate_exist = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=strings.VEHICLE_CONFLICT_REGISTRATION_PLATE_ERROR
    )
    vehicle_create_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.VEHICLE_CREATE_ERROR
    )

    if await check_vin_is_taken(vehicles_repo, vehicle_create.vin):
        raise vehicle_vin_exist

    if await check_registration_plate_is_taken(vehicles_repo, vehicle_create.registration_plate):
        raise vehicle_reg_plate_exist

    try:
        vehicle = await vehicles_repo.create_vehicle_by_user_id(user.id, **vehicle_create.__dict__)
    except EntityCreateError as exception:
        raise vehicle_create_error from exception

    return VehicleInResponse(vehicle=vehicle)


@router.get(
    "",
    response_model=ListOfVehiclesInResponse,
    name="vehicles:get-my-vehicles"
)
async def get_vehicles(
        user: User = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> ListOfVehiclesInResponse:
    vehicles = await vehicles_repo.get_vehicles_by_user_id(user.id)
    return ListOfVehiclesInResponse(vehicles=vehicles, count=len(vehicles))


@router.get(
    "/{vehicle_id}",
    response_model=VehicleInResponse,
    name="vehicles:get-vehicle"
)
async def get_vehicle(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
) -> VehicleInResponse:
    return VehicleInResponse(vehicle=vehicle)


@router.put(
    "/{vehicle_id}",
    response_model=VehicleInResponse,
    name="vehicles:update-vehicle"
)
async def update_vehicle(
        vehicle_update: VehicleInUpdate = Body(..., embed=True, alias="vehicle"),
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        user: User = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> VehicleInResponse:
    vehicle_vin_exist = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=strings.VEHICLE_CONFLICT_VIN_ERROR
    )
    vehicle_reg_plate_exist = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=strings.VEHICLE_CONFLICT_REGISTRATION_PLATE_ERROR
    )
    vehicle_mileage_reduce = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.VEHICLE_MILEAGE_REDUCE
    )
    vehicle_update_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.VEHICLE_UPDATE_ERROR
    )

    if vehicle_update.vin and vehicle_update.vin != vehicle.vin:
        if await check_vin_is_taken(vehicles_repo, vehicle_update.vin):
            raise vehicle_vin_exist

    if vehicle_update.registration_plate and vehicle_update.registration_plate != vehicle.registration_plate:
        if await check_registration_plate_is_taken(vehicles_repo, vehicle_update.registration_plate):
            raise vehicle_reg_plate_exist

    if vehicle_update.mileage and vehicle_update.mileage < vehicle.mileage:
        raise vehicle_mileage_reduce

    try:
        vehicle = await vehicles_repo.update_vehicle_by_id_and_user_id(vehicle.id, user.id, **vehicle_update.__dict__)
    except EntityUpdateError as exception:
        raise vehicle_update_error from exception

    return VehicleInResponse(vehicle=vehicle)


@router.delete(
    "/{vehicle_id}",
    name="vehicles:delete-vehicle",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_vehicle_by_id(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        user: User = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
) -> None:
    vehicle_delete_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.VEHICLE_DELETE_ERROR
    )

    try:
        await vehicles_repo.delete_vehicle_by_id_and_user_id(vehicle.id, user.id)
    except EntityDeleteError as exception:
        raise vehicle_delete_error from exception
