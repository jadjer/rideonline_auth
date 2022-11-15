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

from typing import Optional
from pydantic import BaseModel, HttpUrl

from app.models.domain.user import User
from app.models.domain.profile import Profile, Gender


class ProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Gender = Gender.undefined
    age: Optional[int] = None
    country: Optional[str] = None
    region: Optional[str] = None
    image: Optional[HttpUrl] = None


class ProfileResponse(BaseModel):
    user: User
    profile: Profile
