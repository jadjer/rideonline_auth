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

from datetime import datetime
from pydantic import field_validator, BaseModel, Field, ConfigDict


class BaseAppModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class DateTimeModelMixin(BaseAppModel):
    model_config = ConfigDict(from_attributes=True)

    created_at: datetime = None
    updated_at: datetime = None

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def default_datetime(cls, value: datetime) -> datetime:
        return value


class IDModelMixin(BaseAppModel):
    id: int = Field(0, alias="id")
