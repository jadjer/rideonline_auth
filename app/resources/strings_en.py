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

class StringsEN(object):
    USER_CREATE_ERROR = "User create error"

    USER_DOES_NOT_EXIST_ERROR = "User does not exist"

    INCORRECT_LOGIN_INPUT = "incorrect username or password"
    USERNAME_TAKEN = "User with this username already exists"
    USERNAME_DOES_NOT_EXIST = "User with this username does not exist"
    EMAIL_TAKEN = "User with this email already exists"
    PHONE_NUMBER_TAKEN = "User with this phone already exists"
    PHONE_NUMBER_DOES_NOT_EXIST = "Phone number does not exist"
    PHONE_NUMBER_INVALID_ERROR = "Invalid phone number"

    SMS_SERVICE_TEMPORARY_UNAVAILABLE = "Phone validation service temporary unavailable"
    SEND_SMS_ERROR = "Error sending sms to phone"
    VERIFICATION_CODE = "Your verification code is {code}"
    VERIFICATION_CODE_CREATE_ERROR = "Can't create new verification code to phone number"
    VERIFICATION_CODE_DOES_NOT_EXISTS = "Verification code doesn't exists"
    VERIFICATION_CODE_IS_WRONG = "Verification code is wrong"

    WRONG_TOKEN_PREFIX = "Unsupported authorization type"
    MALFORMED_PAYLOAD = "Could not validate credentials"
    WRONG_TOKEN_PAIR = "Wrong token pair"
    REFRESH_TOKEN_IS_REVOKED = "Refresh token is revoked"

    AUTHENTICATION_REQUIRED = "Authentication required"
