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

from fastapi import status, Depends
from fastapi.openapi.models import APIKey, APIKeyIn
from fastapi.security.api_key import APIKeyBase
from fastapi.exceptions import HTTPException
from fastapi.requests import Request

from app.api.dependencies.get_from_header import get_language
from app.resources import strings_factory


class AuthTokenHeader(APIKeyBase):
    def __init__(
            self,
            name: str,
            scheme_name: str | None = None,
            description: str | None = None,
            auto_error: bool = True
    ):
        self.model: APIKey = APIKey(**{"in": APIKeyIn.header}, name=name, description=description)
        self.scheme_name = scheme_name or self.__class__.__name__
        self.auto_error = auto_error

    async def __call__(self, request: Request, language: str = Depends(get_language)) -> str | None:
        api_key: str = request.headers.get(self.model.name)
        if api_key:
            return api_key

        if not self.auto_error:
            return None

        strings = strings_factory.getLanguage(language)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=strings.AUTHENTICATION_REQUIRED)
