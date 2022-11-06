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
from app.api.dependencies.get_id_from_path import (
    get_reminder_id_from_path,
)
from app.api.dependencies.vehicle import get_vehicle_by_id_from_path
from app.database.errors import (
    EntityCreateError,
    EntityDoesNotExists,
    EntityUpdateError,
    EntityDeleteError,
)
from app.database.repositories.reminders import RemindersRepository
from app.models.domain.vehicle import Vehicle
from app.models.schemas.reminder import (
    ReminderInResponse,
    ListOfRemindersInResponse,
    ReminderInCreate,
    ReminderInUpdate,
)
from app.resources import strings

router = APIRouter()


@router.post(
    "",
    response_model=ReminderInResponse,
    name="reminders:create-reminder",
)
async def create_reminder(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        reminder_create: ReminderInCreate = Body(..., embed=True, alias="reminder"),
        reminders_repo: RemindersRepository = Depends(get_repository(RemindersRepository)),
) -> ReminderInResponse:
    reminder_create_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.REMINDER_CREATE_ERROR
    )

    try:
        reminder = await reminders_repo.create_reminder_by_vehicle_id(vehicle.id, **reminder_create.__dict__)
    except EntityCreateError as exception:
        raise reminder_create_error from exception

    return ReminderInResponse(reminder=reminder)


@router.get(
    "",
    response_model=ListOfRemindersInResponse,
    name="reminders:get-all-reminders"
)
async def get_reminder(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        reminders_repo: RemindersRepository = Depends(get_repository(RemindersRepository)),
) -> ListOfRemindersInResponse:
    reminders = await reminders_repo.get_reminders_by_vehicle_id(vehicle.id)
    return ListOfRemindersInResponse(reminders=reminders, count=len(reminders))


@router.get(
    "/{reminder_id}",
    response_model=ReminderInResponse,
    name="reminders:get-reminder"
)
async def get_reminder_by_id(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        reminder_id: int = Depends(get_reminder_id_from_path),
        reminders_repo: RemindersRepository = Depends(get_repository(RemindersRepository)),
) -> ReminderInResponse:
    reminder_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.REMINDER_DOES_NOT_EXIST_ERROR
    )

    try:
        reminder = await reminders_repo.get_reminder_by_id_and_vehicle_id(reminder_id, vehicle.id)
    except EntityDoesNotExists as exception:
        raise reminder_not_found from exception

    return ReminderInResponse(reminder=reminder)


@router.put(
    "/{reminder_id}",
    response_model=ReminderInResponse,
    name="reminders:update-reminder"
)
async def update_reminder_by_id(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        reminder_id: int = Depends(get_reminder_id_from_path),
        reminder_update: ReminderInUpdate = Body(..., embed=True, alias="reminder"),
        reminders_repo: RemindersRepository = Depends(get_repository(RemindersRepository)),
) -> ReminderInResponse:
    reminder_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.REMINDER_DOES_NOT_EXIST_ERROR
    )
    reminder_update_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.REMINDER_UPDATE_ERROR
    )

    try:
        reminder = await reminders_repo.update_reminder_by_id_and_vehicle_id(
            reminder_id, vehicle.id, **reminder_update.__dict__
        )
    except EntityDoesNotExists as exception:
        raise reminder_not_found from exception
    except EntityUpdateError as exception:
        raise reminder_update_error from exception

    return ReminderInResponse(reminder=reminder)


@router.delete(
    "/{reminder_id}",
    name="reminders:delete-reminder",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_reminder_by_id(
        vehicle: Vehicle = Depends(get_vehicle_by_id_from_path),
        reminder_id: int = Depends(get_reminder_id_from_path),
        reminders_repo: RemindersRepository = Depends(get_repository(RemindersRepository)),
) -> None:
    reminder_not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=strings.REMINDER_DOES_NOT_EXIST_ERROR
    )
    reminder_delete_error = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=strings.REMINDER_DELETE_ERROR
    )

    try:
        await reminders_repo.delete_reminder_by_id_and_vehicle_id(reminder_id, vehicle.id)
    except EntityDoesNotExists as exception:
        raise reminder_not_found from exception
    except EntityDeleteError as exception:
        raise reminder_delete_error from exception
