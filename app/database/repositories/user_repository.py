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
            age: int = 18,
            country: str = "",
            region: str = "",
            image: str = "",
            **kwargs
    ) -> UserInDB | None:
        query = """
            MATCH (phone:Phone {number: $phone})
            CREATE (phone)-[:Attached]->(user:User)
            SET
                user.username = $username,
                user.salt = $salt,
                user.password = $password,
                user.first_name = $first_name,
                user.last_name = $last_name,
                user.age = $age,
                user.gender = $gender,
                user.country = $country,
                user.region = $region,
                user.image = $image,
                user.is_blocked = false
            RETURN id(user) AS user_id
        """

        user = UserInDB(phone=phone, username=username)
        user.change_password(password)

        user.first_name = first_name
        user.last_name = last_name
        user.gender = gender.name
        user.age = age
        user.country = country
        user.region = region
        user.image = image

        result: AsyncResult = await self.session.run(query, **user.__dict__)

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
        query = """
            MATCH (phone:Phone)-[:Attached]->(user:User)
            WHERE id(user) = $user_id
            RETURN id(user) AS user_id, user, phone
        """

        result: AsyncResult = await self.session.run(query, user_id=user_id)
        record: Record | None = await result.single()
        user: UserInDB = self._get_user_from_record(record)

        return user

    async def get_user_by_username(self, username: str) -> UserInDB | None:
        query = """
            MATCH (phone:Phone)-[:Attached]->(user:User {username: $username})
            RETURN id(user) AS user_id, user, phone
        """

        result: AsyncResult = await self.session.run(query, username=username)
        record: Record | None = await result.single()
        user: UserInDB = self._get_user_from_record(record)

        return user

    async def get_user_by_phone(self, phone: str) -> UserInDB | None:
        query = """
            MATCH (phone:Phone {number: $phone})-[:Attached]->(user:User)
            RETURN id(user) AS user_id, user, phone
        """

        result: AsyncResult = await self.session.run(query, phone=phone)
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
            gender: Gender | None = None,
            age: int | None = None,
            country: str | None = None,
            region: str | None = None,
            image: str | None = None,
            **kwargs
    ) -> UserInDB | None:
        user = await self.get_user_by_id(user_id)
        if not user:
            return user

        user.username = username or user.username
        user.first_name = first_name or user.first_name
        user.last_name = last_name or user.last_name
        user.gender = user.gender.name
        user.age = age or user.age
        user.country = country or user.country
        user.region = region or user.region
        user.image = image or user.image

        if gender:
            user.gender = gender.name

        if password:
            user.change_password(password)

        query = """
            MATCH (user:User)
            WHERE id(user) = $id
            SET
                user.username = $username,
                user.salt = $salt,
                user.password = $password,
                user.first_name = $first_name,
                user.last_name = $last_name,
                user.age = $age,
                user.gender = $gender,
                user.country = $country,
                user.region = $region,
                user.image = $image
        """

        await self.session.run(query, **user.__dict__)

        return await self.get_user_by_id(user.id)

    async def change_user_phone_by_user_id(self, user_id: int, *, phone: str) -> UserInDB | None:
        query = """
            MATCH (phone:Phone)-[r:Attached]->(user:User)
            WHERE id(user) = $user_id
            MATCH (newPhone:Phone {number: $phone})
            CREATE (newPhone)-[:Attached]->(user)
            DELETE r
        """

        await self.session.run(query, user_id=user_id, phone=phone)

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
            first_name=record["user"]["first_name"],
            last_name=record["user"]["last_name"],
            age=record["user"]["age"],
            gender=record["user"]["gender"],
            country=record["user"]["country"],
            region=record["user"]["region"],
            image=record["user"]["image"],
            is_blocked=record["user"]["is_blocked"],
        )

        return user
