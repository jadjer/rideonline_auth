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

from pydantic import HttpUrl

from app.models.common import BaseAppModel
from app.models.domain.token import Token
from app.models.domain.user import User, Gender


class Username(BaseAppModel):
    username: str


class UserLogin(BaseAppModel):
    username: str
    password: str


class UserCreate(BaseAppModel):
    phone: str
    username: str
    password: str
    verification_token: str
    verification_code: str
    first_name: str = ""
    last_name: str = ""
    gender: Gender = Gender.undefined
    age: int = 18
    country: str = ""
    region: str = ""
    image: HttpUrl = ""


class UserChangePhone(BaseAppModel):
    phone: str
    verification_token: str
    verification_code: str


class UserChangePassword(BaseAppModel):
    phone: str
    password: str
    verification_token: str
    verification_code: str


class UserUpdate(BaseAppModel):
    username: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    gender: Gender | None = None
    age: int | None = None
    country: str | None = None
    region: str | None = None
    image: HttpUrl | None = None


class UserResponse(BaseAppModel):
    user: User


class UserWithTokenResponse(BaseAppModel):
    user: User
    token: Token
