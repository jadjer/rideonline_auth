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
from pydantic import HttpUrl, EmailStr, BaseModel


class Gender(Enum):
    UNDEFINED = "undefined"
    MALE = "male"
    FEMALE = "female"


class Profile(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    last_name: Optional[str] = None
    gender: Gender = Gender.UNDEFINED
    age: Optional[int] = None

    image: Optional[HttpUrl] = None
