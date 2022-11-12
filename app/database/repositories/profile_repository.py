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

    async def get_profile(self, username) -> Profile | None:
        query = """
            MATCH (user:User {username: $username}) 
            RETURN id(user) AS user_id, user
        """

        result: AsyncResult = await self.session.run(query, username=username)
        record: Optional[Record] = await result.single()

        if not record:
            logger.warning("Query result is empty")
            return None

        profile = Profile()
        profile.first_name = record["user"]["first_name"]
        profile.last_name = record["user"]["last_name"]
        profile.gender = Gender[record["user"]["gender"]]
        profile.age = record["user"]["age"]
        profile.country = record["user"]["country"]
        profile.region = record["user"]["region"]
        profile.image = record["user"]["image"]

        return profile

    async def update_profile(
            self,
            username: str,
            *,
            first_name: Optional[str] = None,
            last_name: Optional[str] = None,
            gender: Gender = Gender.UNDEFINED,
            age: Optional[int] = None,
            country: Optional[str] = None,
            region: Optional[str] = None,
            image: Optional[HttpUrl] = None,
    ) -> Profile | None:
        query = """
            MERGE (user:User {username: $username}) 
            SET user.first_name=$first_name 
            SET user.last_name=$last_name 
            SET user.country=$country 
            SET user.region=$region 
            SET user.age=$age 
            SET user.gender=$gender 
            SET user.image=$image 
            RETURN id(user) AS user_id, user
        """

        result: AsyncResult = await self.session.run(
            query,
            username=username,
            first_name=first_name,
            last_name=last_name,
            country=country,
            region=region,
            age=age,
            gender=gender.name,
            image=image,
        )
        record: Optional[Record] = await result.single()
        if not record:
            return None

        return await self.get_profile(username)
