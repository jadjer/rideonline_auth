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
from neo4j import AsyncResult, Record

from app.database.repositories.base_repository import BaseRepository
from app.models.domain.verification_code import VerificationCode


class PhoneRepository(BaseRepository):
    async def update_verification_code_by_phone(self, phone: str, secret: str, token: str, code: str):
        query = """
            MERGE (phone:Phone {number: $phone})
            SET
                phone.secret = $secret,
                phone.verification_token = $token,
                phone.verification_code = $code
        """

        await self.session.run(query, phone=phone, secret=secret, token=token, code=code)

    async def get_verification_code_by_phone(self, phone: str) -> VerificationCode | None:
        query = """
            MATCH (phone:Phone {number: $phone})
            RETURN
                phone.secret AS secret,
                phone.verification_token AS verification_token,
                phone.verification_code AS verification_code
        """

        result: AsyncResult = await self.session.run(query, phone=phone)
        record: Record | None = await result.single()

        if not record:
            logger.warning("Query result is empty")
            return None

        secret: str = record["secret"]
        verification_token: str = record["verification_token"]
        verification_code: int = record["verification_code"]

        return VerificationCode(
            secret=secret,
            token=verification_token,
            code=verification_code
        )

    async def is_attached_by_phone(self, phone: str) -> bool:
        query = """
               MATCH (phone:Phone {number: $phone})-[:Attached]->()
               RETURN phone
           """

        result: AsyncResult = await self.session.run(query, phone=phone)
        record: Record | None = await result.single()

        if record:
            return True

        return False
