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

from app.database.repositories.base_repository import BaseRepository
from app.models.domain.profile import Profile


class ProfileRepository(BaseRepository):
    async def update_profile(self, username) -> Profile | None:
        query = """
            MERGE (u:User {username: $username}) 
            SET u.secret=$secret 
            RETURN u AS user
        """

        result: AsyncResult = await self.session.run(query, username=username)
        record: Optional[Record] = await result.single()
        if not record:
            return None

        user_record = record["user"]

        profile = Profile()
        if "first_name" in user_record:
            profile.first_name = user_record["first_name"]
        if "last_name" in user_record:
            profile.last_name = user_record["last_name"]
        return profile
