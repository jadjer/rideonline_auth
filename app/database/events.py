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

from fastapi import FastAPI
from loguru import logger

from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession

from app.core.settings.app import AppSettings


async def connect_to_db(app: FastAPI, settings: AppSettings) -> AsyncDriver:
    logger.info("Connecting to Neo4j")

    driver: AsyncDriver = AsyncGraphDatabase.driver(
        settings.get_database_url,
        auth=(
            settings.database_user,
            settings.database_pass
        )
    )
    session: AsyncSession = driver.session()

    app.state.driver = driver
    app.state.session = session

    logger.info("Connection established")

    return driver


async def close_db_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")

    driver: AsyncDriver = app.state.driver
    session: AsyncSession = app.state.session

    await session.close()
    await driver.close()

    logger.info("Connection closed")
