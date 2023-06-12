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

from pydantic import BaseModel, HttpUrl

from app.models.domain.token import Token
from app.models.domain.user import User, Gender


class Username(BaseModel):
    username: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    phone: str
    username: str
    password: str
    verification_token: str
    verification_code: int
    first_name: str | None = None
    last_name: str | None = None
    gender: Gender = Gender.undefined
    age: int | None = None
    country: str | None = None
    region: str | None = None
    image: HttpUrl | None = None


class UserChangePhone(BaseModel):
    phone: str
    verification_code: int
    phone_token: str


class UserChangePassword(BaseModel):
    phone: str
    password: str
    verification_code: int
    phone_token: str


class UserUpdate(BaseModel):
    username: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    gender: Gender = Gender.undefined
    age: int | None = None
    country: str | None = None
    region: str | None = None
    image: HttpUrl | None = None


class UserResponse(BaseModel):
    user: User


class UserWithTokenResponse(BaseModel):
    user: User
    token: Token
