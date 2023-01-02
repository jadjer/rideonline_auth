#  Copyright 2022 Pavel Suprunov
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from fastapi import APIRouter

from . import auth, user, token, profiles, exist

router = APIRouter()

router.include_router(auth.router, tags=["Auth"])
router.include_router(user.router, tags=["Users"], prefix="/users")
router.include_router(token.router, tags=["Tokens"], prefix="/tokens")
router.include_router(profiles.router, tags=["Profiles"], prefix="/profiles")
router.include_router(exist.router, tags=["Exists"], prefix="/exists")
