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

from enum import Enum
from typing import Optional
from pydantic import HttpUrl

from app.models.common import IDModelMixin
from app.services import security


class Gender(Enum):
    undefined = "undefined"
    male = "male"
    female = "female"


class User(IDModelMixin):
    phone: str
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Gender = Gender.undefined
    age: Optional[int] = None
    country: Optional[str] = None
    region: Optional[str] = None
    image: Optional[HttpUrl] = None
    is_blocked: bool = False


class UserInDB(User):
    salt: str = ""
    password: str = ""

    def check_password(self, password: str) -> bool:
        return security.verify_password(self.salt + password, self.password)

    def change_password(self, password: str) -> None:
        self.salt = security.generate_salt()
        self.password = security.get_password_hash(self.salt + password)
