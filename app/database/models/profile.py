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

from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.database.base import Base
from app.models.domain.profile import Gender


class ProfileModel(Base):
    __tablename__ = "profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

    email = Column(String)
    first_name = Column(String)
    second_name = Column(String)
    last_name = Column(String)
    gender = Column(Enum(Gender), default=Gender.UNDEFINED)
    age = Column(Integer)
    image = Column(String)

    user = relationship("UserModel", uselist=False)
