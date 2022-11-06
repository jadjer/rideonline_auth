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
from app.api.dependencies.get_id_from_path import (
    get_service_id_from_path,
)
from app.api.dependencies.vehicle import get_vehicle_by_id_from_path
from app.database.errors import (
    EntityCreateError,
    EntityDoesNotExists,
    EntityUpdateError,
    EntityDeleteError,
)
from app.database.repositories.services import ServicesRepository
from app.database.repositories.vehicles import VehiclesRepository
from app.models.domain.user import User
from app.models.domain.vehicle import Vehicle
from app.models.schemas.service import (
    ServiceInResponse,
    ListOfServicesInResponse,
    ServiceInCreate, ServiceInUpdate,
)
from app.resources import strings
from app.services.vehicles import (
    update_vehicle_mileage,
)

router = APIRouter()


@router.post(
    "",
    response_model=ServiceInResponse,
    name="services:create-service",
)
async def create_service(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        service_create: ServiceInCreate = Body(..., embed=True, alias="service"),
        user: User = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ServiceInResponse:
    vehicle_mileage_reduce = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.VEHICLE_MILEAGE_REDUCE
    )
    service_create_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.SERVICE_CREATE_ERROR
    )

    if service_create.mileage and service_create.mileage < vehicle.mileage:
        raise vehicle_mileage_reduce

    try:
        service = await services_repo.create_service_by_vehicle_id(vehicle.id, **service_create.__dict__)
    except EntityCreateError as exception:
        raise service_create_error from exception

    await update_vehicle_mileage(vehicles_repo, vehicle.id, user.id, service_create.mileage)

    return ServiceInResponse(service=service)


@router.get(
    "",
    response_model=ListOfServicesInResponse,
    name="services:get-all-services"
)
async def get_services(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ListOfServicesInResponse:
    services = await services_repo.get_services_by_vehicle_id(vehicle.id)
    return ListOfServicesInResponse(services=services, count=len(services))


@router.get(
    "/{service_id}",
    response_model=ServiceInResponse,
    name="services:get-service"
)
async def get_service_by_id(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        service_id: int = Depends(get_service_id_from_path),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ServiceInResponse:
    service_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.SERVICE_DOES_NOT_EXIST_ERROR
    )

    try:
        service = await services_repo.get_service_by_id_and_vehicle_id(service_id, vehicle.id)
    except EntityDoesNotExists as exception:
        raise service_not_found from exception

    return ServiceInResponse(service=service)


@router.put(
    "/{service_id}",
    response_model=ServiceInResponse,
    name="services:update-service"
)
async def update_service_by_id(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        service_id: int = Depends(get_service_id_from_path),
        service_update: ServiceInUpdate = Body(..., embed=True, alias="service"),
        user: User = Depends(get_current_user_authorizer()),
        vehicles_repo: VehiclesRepository = Depends(get_repository(VehiclesRepository)),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> ServiceInResponse:
    vehicle_mileage_reduce = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.VEHICLE_MILEAGE_REDUCE
    )
    service_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.SERVICE_DOES_NOT_EXIST_ERROR
    )
    service_update_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.SERVICE_UPDATE_ERROR
    )

    if service_update.mileage and service_update.mileage < vehicle.mileage:
        raise vehicle_mileage_reduce

    try:
        service = await services_repo.update_service_by_id_and_vehicle_id(
            service_id, vehicle.id, **service_update.__dict__
        )
    except EntityDoesNotExists as exception:
        raise service_not_found from exception
    except EntityUpdateError as exception:
        raise service_update_error from exception

    if service_update.mileage:
        await update_vehicle_mileage(vehicles_repo, vehicle.id, user.id, service_update.mileage)

    return ServiceInResponse(service=service)


@router.delete(
    "/{service_id}",
    name="services:delete-vehicle",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_service_by_id(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        service_id: int = Depends(get_service_id_from_path),
        services_repo: ServicesRepository = Depends(get_repository(ServicesRepository)),
) -> None:
    service_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.SERVICE_DOES_NOT_EXIST_ERROR
    )
    service_delete_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.SERVICE_DELETE_ERROR
    )

    try:
        await services_repo.delete_service_by_id_and_vehicle_id(service_id, vehicle.id)
    except EntityDoesNotExists as exception:
        raise service_not_found from exception
    except EntityDeleteError as exception:
        raise service_delete_error from exception
