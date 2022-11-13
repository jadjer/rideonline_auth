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
from neo4j import AsyncResult, Record
from loguru import logger
from pydantic import HttpUrl

from app.database.repositories.base_repository import BaseRepository
from app.models.domain.profile import Profile, Gender


class ProfileRepository(BaseRepository):

    async def get_profile_by_id(self, user_id: int) -> Optional[Profile]:
        query = f"""
            MATCH (user:User)
            WHERE id(user) = {user_id}
            RETURN user
        """
        result: AsyncResult = await self.session.run(query)
        record: Optional[Record] = await result.single()

        if not record:
            logger.warning("Query result is empty")
            return None

        return Profile(
            first_name=record["user"]["first_name"],
            last_name=record["user"]["last_name"],
            gender=Gender[record["user"]["gender"] or "undefined"],
            age=record["user"]["age"],
            country=record["user"]["country"],
            region=record["user"]["region"],
            image=record["user"]["image"],
        )

    async def get_profile_by_username(self, username: str) -> Optional[Profile]:
        query = f"""
            MATCH (user:User)
            WHERE user.username = "{username}"
            RETURN user
        """
        result: AsyncResult = await self.session.run(query)
        record: Optional[Record] = await result.single()

        if not record:
            logger.warning("Query result is empty")
            return None

        return Profile(
            first_name=record["user"]["first_name"],
            last_name=record["user"]["last_name"],
            gender=Gender[record["user"]["gender"]],
            age=record["user"]["age"],
            country=record["user"]["country"],
            region=record["user"]["region"],
            image=record["user"]["image"],
        )

    async def update_profile(
            self,
            user_id: int,
            *,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            gender: Gender = Gender.undefined,
            age: Optional[int] = None,
            country: Optional[str] = None,
            region: Optional[str] = None,
            image: Optional[HttpUrl] = None,
            **kwargs
    ) -> Optional[Profile]:
        profile = await self.get_profile_by_id(user_id)
        profile.first_name = first_name or profile.first_name
        profile.last_name = last_name or profile.last_name
        profile.age = age or profile.age
        profile.gender = gender.name
        profile.country = country or profile.country
        profile.region = region or profile.region
        profile.image = image or profile.image

        query = f"""
            MATCH (user:User)
            WHERE id(user) = {user_id}
            SET user.first_name = $first_name
            SET user.last_name = $last_name
            SET user.age = $age
            SET user.gender = $gender
            SET user.country = $country
            SET user.region = $region
            SET user.image = $image
            RETURN user
        """

        result: AsyncResult = await self.session.run(query, profile.__dict__)
        record: Optional[Record] = await result.single()
        if not record:
            return None

        return await self.get_profile_by_id(user_id)
