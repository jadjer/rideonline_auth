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
    events,
    comments,
    event_confirmations,
)

router = APIRouter()

router.include_router(events.router, tags=["events"], prefix="/events")
router.include_router(event_confirmations.router, tags=["events"], prefix="/events/{event_id}")
router.include_router(comments.router, prefix="/events/{event_id}/comments")
