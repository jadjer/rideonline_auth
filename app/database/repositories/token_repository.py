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
from neo4j import AsyncResult, Record

from app.database.repositories.base_repository import BaseRepository


class TokenRepository(BaseRepository):
    async def get_token(self, user_id: int) -> str | None:
        query = f"""
            MATCH (user:User)
            WHERE id(user) = {user_id}
            RETURN user.token as token
        """

        result: AsyncResult = await self.session.run(query)
        record: Record | None = await result.single()

        if not record:
            return None

        token = record["token"]

        return token

    async def update_token(self, user_id: int, token: str):
        query = f"""
            MATCH (user:User)
            WHERE id(user) = {user_id}
            SET user.token = "{token}"
        """

        await self.session.run(query)
