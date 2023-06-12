#  Copyright 2023 Pavel Suprunov
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
from pyotp import TOTP, random_base32
from neo4j import AsyncResult, Record

from app.models.domain.verification_code import VerificationCode

AUTH_ISSUER = "rideonline_auth"


def create_verification_code(interval: int) -> VerificationCode:
    secret: str = random_base32()
    verification_token: str = random_base32()

    otp = TOTP(secret + verification_token, issuer=AUTH_ISSUER, interval=interval)

    verification_code = otp.now()

    return VerificationCode(
        secret=secret,
        token=verification_token,
        code=verification_code,
    )


def check_verification_code(secret: str, verification_token: str, verification_code: int, interval: int) -> bool:
    otp = TOTP(secret + verification_token, issuer=AUTH_ISSUER, interval=interval)

    is_valid = otp.verify(str(verification_code))
    if is_valid:
        return True

    return False
