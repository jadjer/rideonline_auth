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

from random import randrange
from typing import List
from sqlalchemy import select, and_

from app.database.errors import (
    EntityDoesNotExists,
    EntityDeleteError,
    EntityCreateError, EntityUpdateError,
)
from app.database.models import VerificationCodeModel
from app.database.repositories.base import BaseRepository


class VerificationRepository(BaseRepository):

    async def create_verification_code_by_phone(self, phone: str) -> int:
        new_verification_code = VerificationCodeModel()
        new_verification_code.phone = phone
        new_verification_code.verification_code = randrange(100000, 999999)

        self.session.add(new_verification_code)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityCreateError from exception

        return new_verification_code.verification_code

    async def get_verification_code_by_phone_and_code(self, phone: str, verification_code: int) -> int:
        verification_code_in_db: VerificationCodeModel = await self._get_verification_code_by_phone_and_code(
            phone, verification_code
        )
        if not verification_code_in_db:
            raise EntityDoesNotExists

        return verification_code_in_db.verification_code

    async def mark_as_verified_by_phone_and_verification_code(self, phone: str, verification_code: int) -> None:
        verification_code_in_db: VerificationCodeModel = await self._get_verification_code_by_phone_and_code(
            phone, verification_code
        )
        verification_code_in_db.is_verified = True

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityUpdateError from exception

    async def delete_verification_code_by_phone_and_code(self, phone: str, verification_code: int) -> None:
        verification_code_in_db = await self._get_verification_code_by_phone_and_code(phone, verification_code)

        try:
            await self.session.delete(verification_code_in_db)
            await self.session.commit()
        except Exception as exception:
            raise EntityDeleteError from exception

    async def delete_verification_codes_by_phone(self, phone: str) -> None:
        verification_codes_in_db = await self._get_verification_codes_by_phone(phone)

        for verification_code_in_db in verification_codes_in_db:
            await self.session.delete(verification_code_in_db)

        try:
            await self.session.commit()
        except Exception as exception:
            raise EntityDeleteError from exception

    async def _get_verification_code_by_phone_and_code(
            self,
            phone: str,
            verification_code: int
    ) -> VerificationCodeModel:
        query = select(VerificationCodeModel).where(
            and_(
                VerificationCodeModel.phone == phone,
                VerificationCodeModel.verification_code == verification_code,
                VerificationCodeModel.is_verified == False
            )
        )
        result = await self.session.execute(query)

        verification_code_in_db: VerificationCodeModel = result.scalars().first()
        if not verification_code_in_db:
            raise EntityDoesNotExists

        return verification_code_in_db

    async def _get_verification_codes_by_phone(self, phone: str) -> List[VerificationCodeModel]:
        query = select(VerificationCodeModel).where(
            and_(
                VerificationCodeModel.phone == phone,
                VerificationCodeModel.is_verified == False
            )
        )
        result = await self.session.execute(query)

        verification_codes_in_db: VerificationCodeModel = result.scalars().all()

        return verification_codes_in_db
