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
from pyotp import TOTP, random_base32
from neo4j import AsyncResult, Record

from app.database.repositories.base import BaseRepository


class PhoneRepository(BaseRepository):

    async def create_verification_code(self, phone: str) -> str:
        query = """
            MERGE (p:Phone {phone: $phone}) 
            SET p.secret=$secret
        """

        secret = random_base32()

        await self.session.run(query, phone=phone, secret=secret)

        otp = TOTP(secret)
        verification_code = otp.now()

        print(f"Code: {verification_code}")

        return verification_code

    async def verify_code(self, phone: str, verification_code: int) -> bool:
        query = """
            MATCH (p:Phone {phone: $phone}) 
            RETURN p.secret AS secret
        """

        result: AsyncResult = await self.session.run(query, phone=phone)
        record: Optional[Record] = await result.single()

        if not record:
            return False

        secret = record["secret"]
        otp = TOTP(secret)

        is_valid = otp.verify(str(verification_code))
        if is_valid:
            return True

        return False

    async def is_attached(self, phone: str) -> bool:
        query = """
            MATCH (p:Phone {phone: $phone})-[:Attached]-() 
            RETURN p
        """

        result: AsyncResult = await self.session.run(query, phone=phone)
        record: Optional[Record] = await result.single()

        if record:
            return True

        return False
