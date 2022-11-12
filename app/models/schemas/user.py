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

from pydantic import BaseModel

from app.models.domain.user import User


class PhoneVerification(BaseModel):
    phone: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    phone: str
    password: str
    verification_code: int


class UserChangeUsername(BaseModel):
    username: str
    verification_code: int


class UserChangePhone(BaseModel):
    phone: str
    verification_code: int


class Token(BaseModel):
    token_access: str
    token_refresh: str


class UserResponse(BaseModel):
    user: User


class UserResponseWithToken(BaseModel):
    user: User
    token: Token
