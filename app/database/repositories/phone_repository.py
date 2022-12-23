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

from typing import Optional
from loguru import logger
from pyotp import TOTP, random_base32
from neo4j import AsyncResult, Record

from app.database.repositories.base_repository import BaseRepository


class PhoneRepository(BaseRepository):

    async def create_verification_code_by_phone(self, phone: str) -> (str, str):
        secret: str = random_base32()
        token: str = random_base32()

        query = f"""
            MERGE (phone:Phone {{number: "{phone}"}})
            SET phone.secret = "{secret}"
        """

        await self.session.run(query)

        otp = TOTP(secret + token)
        verification_code = otp.now()

        return verification_code, token

    async def verify_phone_by_code_and_token(self, phone: str, verification_code: int, token: str) -> bool:
        query = f"""
            MATCH (phone:Phone)
            WHERE phone.number = "{phone}"
            RETURN phone.secret AS secret
        """

        result: AsyncResult = await self.session.run(query)
        record: Optional[Record] = await result.single()

        if not record:
            logger.warning("Query result is empty")
            return False

        secret: str = record["secret"]

        otp = TOTP(secret + token)

        is_valid = otp.verify(str(verification_code))
        if is_valid:
            return True

        return False

    async def is_attached_by_phone(self, phone: str) -> bool:
        query = """
            MATCH (phone:Phone {number: $phone})-[:Attached]->()
            RETURN phone
        """

        result: AsyncResult = await self.session.run(query, phone=phone)
        record: Optional[Record] = await result.single()

        if record:
            return True

        return False
