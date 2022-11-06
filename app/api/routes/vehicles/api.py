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

from fastapi import APIRouter

from . import (
    fuels,
    reminders,
    services,
    vehicles,
)

router = APIRouter()

router.include_router(vehicles.router, prefix="/vehicles")
router.include_router(fuels.router, prefix="/vehicles/{vehicle_id}/fuels")
router.include_router(services.router, prefix="/vehicles/{vehicle_id}/services")
router.include_router(reminders.router, prefix="/vehicles/{vehicle_id}/reminders")
