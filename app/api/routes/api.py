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
    authentication,
    users,
    profiles,
    services_types,
    vehicles,
    locations,
    posts,
    events
)

router = APIRouter()

router.include_router(authentication.router, tags=["authentication"], prefix="/auth")
router.include_router(users.router, tags=["users"], prefix="/user")
router.include_router(profiles.router, tags=["profiles"], prefix="/profiles")
router.include_router(services_types.router, tags=["services_types"], prefix="/services/types")
router.include_router(vehicles.router, tags=["vehicles"])
router.include_router(locations.router, tags=["locations"], prefix="/locations")
router.include_router(posts.router, tags=["posts"])
router.include_router(events.router, tags=["events"])
