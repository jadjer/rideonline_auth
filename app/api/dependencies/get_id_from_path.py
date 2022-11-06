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

from fastapi import Path


def get_user_id_from_path(user_id: int = Path(..., ge=1)) -> int:
    return user_id


def get_comment_id_from_path(comment_id: int = Path(..., ge=1)) -> int:
    return comment_id


def get_event_id_from_path(event_id: int = Path(..., ge=1)) -> int:
    return event_id


def get_location_id_from_path(location_id: int = Path(..., ge=1)) -> int:
    return location_id


def get_post_id_from_path(post_id: int = Path(..., ge=1)) -> int:
    return post_id


def get_service_id_from_path(service_id: int = Path(..., ge=1)) -> int:
    return service_id


def get_service_type_id_from_path(service_type_id: int = Path(..., ge=1)) -> int:
    return service_type_id


def get_reminder_id_from_path(reminder_id: int = Path(..., ge=1)) -> int:
    return reminder_id
