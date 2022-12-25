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

from pydantic import BaseModel

from app.models.domain.token import Token
from app.models.domain.user import User


class Username(BaseModel):
    username: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    phone: str
    username: str
    password: str
    verification_code: int
    phone_token: str


class UserUpdate(BaseModel):
    username: Optional[str] = None
    phone: Optional[str] = None
    password: Optional[str] = None
    verification_code: int
    phone_token: str


class UserResponse(BaseModel):
    user: User


class UserWithTokenResponse(BaseModel):
    user: User
    token: Token
