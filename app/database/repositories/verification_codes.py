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
from app.database.repositories.base import BaseRepository


class VerificationRepository(BaseRepository):

    async def create_verification_code_by_phone(self, phone: str) -> int:
        verification_code = randrange(100000, 999999)

        query = f"MERGE (p:PhoneVerification {{phone: {phone}}}) " \
                f"SET p.verification_code={verification_code}, p.is_verified={False} " \
                f"RETURN p;"

        await self.session.run(query)

        return verification_code
