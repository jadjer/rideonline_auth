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
    HTTPException,
    status,
)

from app.api.dependencies.database import get_repository
from app.api.dependencies.get_id_from_path import get_service_type_id_from_path
from app.database.errors import EntityDoesNotExists
from app.database.repositories.services_types import ServicesTypesRepository
from app.models.schemas.service_type import (
    ServiceTypeInResponse,
    ListOfServicesTypesInResponse,
)
from app.resources import strings

router = APIRouter()


@router.get(
    "",
    response_model=ListOfServicesTypesInResponse,
    name="services-types:get-all-vehicles"
)
async def get_service_types(
        services_types_repo: ServicesTypesRepository = Depends(get_repository(ServicesTypesRepository)),
) -> ListOfServicesTypesInResponse:
    services_types = await services_types_repo.get_services_types()
    return ListOfServicesTypesInResponse(services_types=services_types, count=len(services_types))


@router.get(
    "/{service_type_id}",
    response_model=ServiceTypeInResponse,
    name="services-types:get-vehicle"
)
async def get_service_type(
        service_type_id: int = Depends(get_service_type_id_from_path),
        services_types_repo: ServicesTypesRepository = Depends(get_repository(ServicesTypesRepository)),
) -> ServiceTypeInResponse:
    type_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.SERVICE_TYPE_DOES_NOT_EXIST_ERROR
    )

    try:
        service_type = await services_types_repo.get_service_type_by_id(service_type_id)
    except EntityDoesNotExists as exception:
        raise type_not_found from exception

    return ServiceTypeInResponse(service_type=service_type)
