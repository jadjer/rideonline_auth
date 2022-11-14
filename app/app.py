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

from fastapi import FastAPI
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors.http_error import http_error_handler
from app.api.routes.api import router as api_router
from app.core.config import get_app_settings
from app.core.events import create_start_app_handler, create_stop_app_handler


def get_application() -> FastAPI:
    settings = get_app_settings()
    settings.configure_logging()

    if settings.debug:
        application = FastAPI(**settings.fastapi_kwargs)
    else:
        application = FastAPI(docs_url=None, redoc_url=None)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_hosts,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.add_event_handler(
        "startup",
        create_start_app_handler(application, settings),
    )
    application.add_event_handler(
        "shutdown",
        create_stop_app_handler(application),
    )

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(404, http_error_handler)

    application.include_router(api_router, prefix=settings.api_prefix)

    @application.get("/")
    async def health():
        return {"health": randrange(100000, 999999)}

    return application


app: FastAPI = get_application()
