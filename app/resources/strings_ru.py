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

from .strings_en import StringsEN


class StringsRU(StringsEN):
    USER_CREATE_ERROR = "Ошибка создания нового пользователя"

    USER_DOES_NOT_EXIST_ERROR = "Пользователь не найден"

    INCORRECT_LOGIN_INPUT = "Неверный username или password"
    USERNAME_TAKEN = "Пользователь с указанным username существует"
    USERNAME_DOES_NOT_EXIST = "Пользователь с указанным username не найден"
    EMAIL_TAKEN = "Пользователь с указанным email существует"
    PHONE_NUMBER_TAKEN = "Пользователь с указанным номером телефона существует"
    PHONE_NUMBER_DOES_NOT_EXIST = "Пользователь с указанным номером телефона не найден"
    PHONE_NUMBER_INVALID_ERROR = "Неверный номер телефона"

    SMS_SERVICE_TEMPORARY_UNAVAILABLE = "Сервис отправки сообщений временно не доступен"
    SEND_SMS_ERROR = "Ошибка отправки смс с кодом подтверждеиня на номер телефона"
    VERIFICATION_CODE = "Код подтверждения {code}"
    VERIFICATION_CODE_CREATE_ERROR = "Не удалось создать новый код подтверждения для номера телефона"
    VERIFICATION_CODE_DOES_NOT_EXISTS = "Код подтверждения не найден"
    VERIFICATION_CODE_IS_WRONG = "Неверный код подтверждения"

    WRONG_TOKEN_PREFIX = "Неподдерживаемый тип авторизации"
    MALFORMED_PAYLOAD = "Не действительные данные для входа"
    WRONG_TOKEN_PAIR = "Не верная пара токенов"
    REFRESH_TOKEN_IS_REVOKED = "Refresh token отозван"

    AUTHENTICATION_REQUIRED = "Требуется авторизация"
