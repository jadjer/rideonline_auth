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

from typing import Optional, List

from pydantic import EmailStr, HttpUrl, BaseModel, Field

from app.models.domain.profile import Gender, Profile

DEFAULT_PROFILES_LIMIT = 100
DEFAULT_PROFILES_OFFSET = 0


class ProfileInCreate(BaseModel):
    email: EmailStr
    first_name: str
    second_name: str
    last_name: str
    gender: Gender = Gender.UNDEFINED
    age: int
    image: HttpUrl


class ProfileInUpdate(BaseModel):
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Optional[Gender] = Gender.UNDEFINED
    age: Optional[int] = None
    image: Optional[HttpUrl] = None


class ProfileInResponse(BaseModel):
    profile: Profile


class ListOfProfileInResponse(BaseModel):
    profiles: List[Profile]
    count: int


class ProfilesFilter(BaseModel):
    limit: int = Field(DEFAULT_PROFILES_LIMIT, ge=1)
    offset: int = Field(DEFAULT_PROFILES_OFFSET, ge=0)
