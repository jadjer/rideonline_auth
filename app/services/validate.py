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

from loguru import logger
from phonenumbers import (
    NumberParseException,
    parse,
    is_possible_number,
    is_valid_number,
)
from pydantic import EmailStr

from app.database.errors import EntityDoesNotExists
from app.database.repositories.users import UsersRepository


def check_phone_is_valid(phone_number: str) -> bool:
    try:
        phone = parse(phone_number, None)
    except NumberParseException:
        logger.warning(f"Phone number {phone_number} parser error")
        return False

    if not is_possible_number(phone):
        logger.warning(f"Phone number {phone_number} is inpossible number")
        return False

    if not is_valid_number(phone):
        logger.warning(f"Phone number {phone_number} is invalid number")
        return False

    return True


async def check_phone_is_taken(repo: UsersRepository, phone: str) -> bool:
    try:
        await repo.get_user_by_phone(phone)
    except EntityDoesNotExists:
        return False

    return True


async def check_username_is_taken(repo: UsersRepository, username: str) -> bool:
    try:
        await repo.get_user_by_username(username)
    except EntityDoesNotExists:
        return False

    return True


async def check_email_is_taken(repo: UsersRepository, email: EmailStr) -> bool:
    try:
        await repo.get_user_by_email(email=email)
    except EntityDoesNotExists:
        return False

    return True
