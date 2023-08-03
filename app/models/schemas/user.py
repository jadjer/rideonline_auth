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

from pydantic import BaseModel, HttpUrl, ConfigDict

from app.models.domain.token import Token
from app.models.domain.user import User, UserInDB, Gender


class Username(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str


class UserLogin(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    password: str


class UserCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class UserChangePhone(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    phone: str
    verification_token: str
    verification_code: str


class UserChangePassword(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    phone: str
    password: str
    verification_token: str
    verification_code: str


class UserUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    gender: Gender | None = None
    age: int | None = None
    country: str | None = None
    region: str | None = None
    image: HttpUrl | None = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: User


class UserWithTokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: User
    token: Token
