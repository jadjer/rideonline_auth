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

from functools import lru_cache
from app.core.settings.app import AppSettings


@lru_cache
def get_app_settings() -> AppSettings:
    config = AppSettings()

    with open(config.public_key_path) as f:
        config.public_key = f.read()

    with open(config.private_key_path) as f:
        config.private_key = f.read()

    return config
