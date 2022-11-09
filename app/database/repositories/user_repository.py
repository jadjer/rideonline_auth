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

from neo4j import Record, AsyncResult, AsyncTransaction
from neo4j.graph import Node

from app.database.repositories.base import BaseRepository
from app.models.domain.user import User


class UserRepository(BaseRepository):

    async def create_user(self, username: str, phone: str) -> User | None:
        async def create_user_node(tx) -> User | None:
            query = """
                CREATE (u:User {username: $username}) 
                RETURN u AS user
            """

            result: AsyncResult = await tx.run(query, username=username)
            record: Record | None = await result.single()

            if not record:
                await transaction.rollback()
                return None

            return self._get_user_from_record(record)

        async def attache_phone_for_user(tx):
            query = """
                MATCH (u:User {username: $username}), (p:Phone {phone: $phone}) 
                CREATE (p)-[:Attached]->(u)
            """

            await tx.run(query, username=username, phone=phone)

        transaction: AsyncTransaction = await self.session.begin_transaction()

        user = await create_user_node(transaction)
        await attache_phone_for_user(transaction)

        await transaction.commit()
        await transaction.close()

        return user

    async def get_user_by_id(self, user_id: int) -> User:
        query = """
            MATCH (u:User) 
            WHERE id(u)=$user_id 
            RETURN u AS user
        """
        return await self._get_user(query, user_id=user_id)

    async def get_user_by_username(self, username: str) -> User:
        query = """
            MATCH (u:User {username: $username}) 
            RETURN u AS user
        """
        return await self._get_user(query, username=username)

    async def get_user_by_phone(self, phone: str) -> User:
        query = """
            MATCH (u:User)<-[:Attached]-(p:Phone {phone: $phone}) 
            RETURN u AS user
        """
        return await self._get_user(query, phone=phone)

    async def is_exists(self, username: str) -> bool:
        user: User | None = await self.get_user_by_username(username)
        if user:
            return True

        return False

    async def _get_user(self, query: str, **kwargs) -> User | None:
        transaction: AsyncTransaction = await self.session.begin_transaction()

        result: AsyncResult = await transaction.run(query, kwargs)
        record: Record | None = await result.single()

        if not record:
            await transaction.rollback()
            return None

        await transaction.commit()
        await transaction.close()

        return self._get_user_from_record(record)

    def _get_user_from_record(self, record: Record) -> User:
        user_data: Node = record["user"]

        user = User(username=user_data["username"])

        if "is_blocked" in user_data.keys():
            user.is_blocked = user_data["is_blocked"]

        return user
