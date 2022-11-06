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

from pydantic import HttpUrl, EmailStr
from sqlalchemy.future import select

from app.database.errors import (
    EntityCreateError,
    EntityUpdateError,
    EntityDoesNotExists
)
from app.database.repositories.base import BaseRepository
from app.models.domain.profile import Gender, Profile
from app.database.models import ProfileModel, UserModel
from app.models.domain.user import UserInDB


class ProfilesRepository(BaseRepository):

    async def create_profile_by_user_id(
            self,
            user_id: int,
            *,
            email: Optional[EmailStr] = None,
            first_name: Optional[str] = None,
            second_name: Optional[str] = None,
            last_name: Optional[str] = None,
            gender: Optional[Gender] = None,
            age: Optional[int] = None,
            image: Optional[HttpUrl] = None,
    ) -> Profile:
        new_profile = ProfileModel()
        new_profile.user_id = user_id
        new_profile.email = email
        new_profile.first_name = first_name
        new_profile.second_name = second_name
        new_profile.last_name = last_name
        new_profile.gender = gender
        new_profile.age = age
        new_profile.image = image

        self.session.add(new_profile)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityCreateError from exception

        return Profile(**new_profile.__dict__)

    async def get_profile_by_user_id(self, user_id: int) -> Profile:
        profile_in_db = await self._get_profile_model_by_user_id(user_id)
        if not profile_in_db:
            raise EntityDoesNotExists

        return Profile(**profile_in_db.__dict__)

    async def get_profile_by_username(self, username: str) -> Profile:
        query = select(ProfileModel).where(ProfileModel.username == username)
        result = await self.session.execute(query)

        profile_in_db: ProfileModel = result.scalars().first()
        if not profile_in_db:
            raise EntityDoesNotExists

        return Profile(**profile_in_db.__dict__)

    async def get_profiles_with_filter(self, limit: int, offset: int) -> List[Profile]:
        query = select(ProfileModel).limit(limit).offset(offset)
        result = await self.session.execute(query)

        profiles_in_db = result.scalars().all()

        return [Profile(**profile_in_db.__dict__) for profile_in_db in profiles_in_db]

    async def update_profile_by_user_id(
            self,
            user_id: int,
            *,
            email: Optional[EmailStr] = None,
            first_name: Optional[str] = None,
            second_name: Optional[str] = None,
            last_name: Optional[str] = None,
            gender: Optional[Gender] = None,
            age: Optional[int] = None,
            image: Optional[HttpUrl] = None,
    ) -> Profile:
        profile_in_db = await self._get_profile_model_by_user_id(user_id)
        profile_in_db.email = email or profile_in_db.email
        profile_in_db.first_name = first_name or profile_in_db.first_name
        profile_in_db.second_name = second_name or profile_in_db.second_name
        profile_in_db.last_name = last_name or profile_in_db.last_name
        profile_in_db.gender = gender or profile_in_db.gender
        profile_in_db.age = age or profile_in_db.age
        profile_in_db.image = image or profile_in_db.image

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityUpdateError from exception

        return Profile(**profile_in_db.__dict__)

    async def _get_profile_model_by_user_id(self, user_id: int) -> ProfileModel:
        query = select(ProfileModel).where(ProfileModel.user_id == user_id)
        result = await self.session.execute(query)

        profile = result.scalars().first()
        if not profile:
            raise EntityDoesNotExists

        return profile
