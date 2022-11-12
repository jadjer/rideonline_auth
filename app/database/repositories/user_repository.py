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

from loguru import logger

from neo4j import Record, AsyncResult
from neo4j.exceptions import ConstraintError

from app.database.repositories.base_repository import BaseRepository
from app.models.domain.user import User, UserInDB


class UserRepository(BaseRepository):

    async def create_user(self, username: str, phone: str, password: str) -> User | None:
        query = """
            MERGE (phone:Phone { number: $phone }) 
            CREATE (user:User { username: $username, password: $password, salt: $salt, is_blocked: $is_blocked }) 
            CREATE (phone)-[:Attached]->(user) 
            RETURN id(user) AS user_id, user, phone
        """

        user = UserInDB(username=username, phone=phone)
        user.change_password(password)

        result: AsyncResult = await self.session.run(
            query,
            phone=phone,
            username=user.username,
            password=user.password,
            salt=user.salt,
            is_blocked=user.is_blocked
        )

        try:
            record: Record | None = await result.single()
        except ConstraintError as exception:
            logger.warning(exception)
            return None

        if not record:
            logger.warning("Query result is empty")
            return None

        user.id = record["user_id"]

        return user

    async def get_user_by_username(self, username: str) -> UserInDB | None:
        query = """
            MATCH (phone:Phone)-[:Attached]->(user:User {username: $username}) 
            RETURN id(user) AS user_id, user, phone
        """

        result: AsyncResult = await self.session.run(query, username=username)
        record: Record | None = await result.single()

        if not record:
            return None

        user = UserInDB(
            id=record["user_id"],
            phone=record["phone"]["number"],
            username=record["user"]["username"],
            password=record["user"]["password"],
            salt=record["user"]["salt"],
            is_blocked=record["user"]["is_blocked"],
        )

        return user

    async def is_exists(self, username: str) -> bool:
        user: User | None = await self.get_user_by_username(username)
        if user:
            return True

        return False
