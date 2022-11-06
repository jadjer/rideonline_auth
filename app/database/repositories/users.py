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

from neo4j import AsyncResult

from app.database.errors import (
    EntityDoesNotExists,
    EntityCreateError,
    EntityUpdateError,
)
from app.database.repositories.base import BaseRepository
from app.models.domain.user import UserInDB


class UsersRepository(BaseRepository):

    async def create_user(
            self,
            username: str,
            phone: str,
            password: str,
    ):
        user: UserInDB = UserInDB(username=username, phone=phone)
        user.change_password(password)

        query = f"CREATE (u:User {user.dict()});"

        try:
            result: AsyncResult = await self.session.run(query)
        except Exception as exception:
            raise EntityCreateError from exception

        # return await self.get_user_by_id(new_user.id)

    async def get_user_by_id(self, user_id: int) -> UserInDB:
        # user_in_db: UserModel = await self._get_user_model_by_id(user_id)
        # if not user_in_db:
        #     raise EntityDoesNotExists
        #
        # return self._convert_user_model_to_model(user_in_db)
        pass

    async def get_user_by_email(self, email: str) -> UserInDB:
        # query = select(UserModel).where(UserModel.email == email)
        # result = await self.session.execute(query)
        #
        # user_in_db = result.scalars().first()
        # if not user_in_db:
        #     raise EntityDoesNotExists
        #
        # return self._convert_user_model_to_model(user_in_db)
        pass

    async def get_user_by_username(self, username: str) -> UserInDB:
        # query = select(UserModel).where(UserModel.username == username)
        # result = await self.session.execute(query)
        #
        # user_in_db = result.scalars().first()
        # if not user_in_db:
        #     raise EntityDoesNotExists
        #
        # return self._convert_user_model_to_model(user_in_db)
        pass

    async def get_user_by_phone(self, phone: str) -> UserInDB:
        # query = select(UserModel).where(UserModel.phone == phone)
        # result = await self.session.execute(query)
        #
        # user_in_db = result.scalars().first()
        # if not user_in_db:
        #     raise EntityDoesNotExists
        #
        # return self._convert_user_model_to_model(user_in_db)
        pass

    async def update_user_by_user(
            self,
            user_id: int,
            *,
            username: Optional[str] = None,
            phone: Optional[str] = None,
            password: Optional[str] = None,

    ) -> UserInDB:
        # user_in_db = await self._get_user_model_by_id(user_id)
        # user_in_db.username = username or user_in_db.username
        # user_in_db.phone = phone or user_in_db.phone
        #
        # if password:
        #     user = UserInDB(**user_in_db.__dict__)
        #     user.change_password(password)
        #
        #     user_in_db.salt = user.salt
        #     user_in_db.password = user.password
        #
        # try:
        #     await self.session.commit()
        # except Exception as exception:
        #     raise EntityUpdateError from exception
        #
        # return await self.get_user_by_id(user_id)
        pass

    async def _get_user_model_by_id(self, user_id: int):
        # user_in_db: UserModel = await self.session.get(UserModel, user_id)
        # if not user_in_db:
        #     raise EntityDoesNotExists
        #
        # return user_in_db
        pass

    @staticmethod
    def _convert_user_model_to_model(user_model) -> UserInDB:
        return UserInDB(
            id=user_model.id,
            username=user_model.username,
            phone=user_model.phone,
            salt=user_model.salt,
            password=user_model.password,
            is_admin=user_model.is_admin,
            is_blocked=user_model.is_blocked,
        )
