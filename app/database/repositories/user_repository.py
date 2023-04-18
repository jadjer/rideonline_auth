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

from loguru import logger

from neo4j import Record, AsyncResult
from neo4j.exceptions import ConstraintError
from pydantic import HttpUrl

from app.database.repositories.base_repository import BaseRepository
from app.models.domain.user import User, UserInDB, Gender


class UserRepository(BaseRepository):
    async def create_user(
            self,
            phone: str,
            username: str,
            password: str,
            *,
            first_name: str = "",
            last_name: str = "",
            gender: Gender = Gender.undefined,
            age: int = 0,
            country: str = "",
            region: str = "",
            image: HttpUrl = "",
            **kwargs
    ) -> UserInDB | None:
        user = UserInDB(username=username, phone=phone)
        user.change_password(password)

        user.first_name = first_name
        user.last_name = last_name
        user.gender = gender.name
        user.age = age
        user.country = country
        user.region = region
        user.image = image

        query = f"""
            MATCH (phone:Phone)
            WHERE phone.number = $phone
            CREATE (phone)-[:Attached]->(user:User)
            SET user.username = $username
            SET user.salt = $salt
            SET user.password = $password
            SET user.first_name = $first_name
            SET user.last_name = $last_name
            SET user.age = $age
            SET user.gender = $gender
            SET user.country = $country
            SET user.region = $region
            SET user.image = $image
            SET user.is_blocked = false
            RETURN id(user) AS user_id
        """

        result: AsyncResult = await self.session.run(query, user.__dict__)

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

    async def get_user_by_id(self, user_id: int) -> UserInDB | None:
        query = f"""
            MATCH (phone:Phone)-[:Attached]->(user:User)
            WHERE id(user) = {user_id}
            RETURN id(user) AS user_id, user, phone
        """

        result: AsyncResult = await self.session.run(query)
        record: Record | None = await result.single()
        user: UserInDB = self._get_user_from_record(record)

        return user

    async def get_user_by_username(self, username: str) -> UserInDB | None:
        query = f"""
            MATCH (phone:Phone)-[:Attached]->(user:User)
            WHERE user.username = "{username}"
            RETURN id(user) AS user_id, user, phone
        """

        result: AsyncResult = await self.session.run(query)
        record: Record | None = await result.single()
        user: UserInDB = self._get_user_from_record(record)

        return user

    async def get_user_by_phone(self, phone: str) -> UserInDB | None:
        query = f"""
            MATCH (phone:Phone)-[:Attached]->(user:User)
            WHERE phone.number = "{phone}"
            RETURN id(user) AS user_id, user, phone
        """

        result: AsyncResult = await self.session.run(query)
        record: Record | None = await result.single()
        user: UserInDB = self._get_user_from_record(record)

        return user

    async def is_exists(self, username: str) -> bool:
        user: User | None = await self.get_user_by_username(username)
        if user:
            return True

        return False

    async def update_user_by_user_id(
            self,
            user_id: int,
            *,
            username: str | None = None,
            password: str | None = None,
            first_name: str | None = None,
            last_name: str | None = None,
            gender: Gender = Gender.undefined,
            age: int | None = None,
            country: str | None = None,
            region: str | None = None,
            image: HttpUrl | None = None,
            **kwargs
    ) -> UserInDB | None:
        user = await self.get_user_by_id(user_id)
        if not user:
            return user

        user.username = username or user.username
        user.first_name = first_name or user.first_name
        user.last_name = last_name or user.last_name
        user.age = age or user.age
        user.country = country or user.country
        user.region = region or user.region
        user.image = image or user.image

        if gender != Gender.undefined:
            user.gender = gender.name

        if password:
            user.change_password(password)

        query = f"""
            MATCH (user:User)
            WHERE id(user) = {user.id}
            SET user.username = "{user.username}"
            SET user.salt = "{user.salt}"
            SET user.password = "{user.password}"
        """

        await self.session.run(query)

        return await self.get_user_by_id(user.id)

    async def change_user_phone_by_user_id(self, user_id: int, *, phone: str) -> UserInDB | None:
        query = f"""
            MATCH (phone:Phone)-[r:Attached]->(user:User)
            WHERE id(user) = {user_id}
            MATCH (newPhone:Phone)
            WHERE newPhone.number = "{phone}"
            CREATE (newPhone)-[:Attached]->(user)
            DELETE r
        """

        await self.session.run(query)

        return await self.get_user_by_id(user_id)

    @staticmethod
    def _get_user_from_record(record: Record) -> UserInDB | None:
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
