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
    HTTPException,
)

from app.api.dependencies.database import get_repository
from app.api.dependencies.get_id_from_path import get_location_id_from_path
from app.database.errors import EntityDoesNotExists
from app.database.repositories.locations import LocationsRepository
from app.models.schemas.location import LocationInResponse
from app.resources import strings

router = APIRouter()


@router.get(
    "/{location_id}",
    response_model=LocationInResponse,
    name="locations:get-location",
)
async def get_location(
        location_id: int = Depends(get_location_id_from_path),
        locations_repo: LocationsRepository = Depends(get_repository(LocationsRepository)),
) -> LocationInResponse:
    location_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.LOCATION_DOES_NOT_EXIST_ERROR
    )

    try:
        location = await locations_repo.get_location_by_id(location_id)
    except EntityDoesNotExists as exception:
        raise location_not_found from exception

    return LocationInResponse(location=location)
