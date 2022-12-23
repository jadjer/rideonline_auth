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

from httpx import AsyncClient
from pydantic import HttpUrl

from app.models.schemas.sms import SmsRequest


async def send_verify_code_to_phone(sms_service: HttpUrl, phone: str, code: str) -> bool:
    headers = {"Content-Type": "application/json"}
    request = SmsRequest(phone=phone, message=f"Your verification code is {code}")
    request_json = request.json()

    print(sms_service)
    print(request_json)

    async with AsyncClient(base_url=sms_service, headers=headers) as client:
        response = await client.post("/send", json=request_json)
        if response.status_code == 200:
            return True

        return False
