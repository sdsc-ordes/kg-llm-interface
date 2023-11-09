# kg-llm-interface
# Copyright 2023 - Swiss Data Science Center (SDSC)
# A partnership between École Polytechnique Fédérale de Lausanne (EPFL) and
# Eidgenössische Technische Hochschule Zürich (ETHZ).
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid


class Message(BaseModel):
    text: str
    time: datetime
    sender: str
    triples: str | None = None


class Conversation(BaseModel):
    """A conversation, represented as a list of messages
    and a unique identifier (uid)."""

    thread: list[Message]
    uid: str | None = str(uuid.uuid4())

    @property
    def start_time(self) -> datetime | None:
        try:
            return self.thread[0].time
        except IndexError:
            return None

    @property
    def end_time(self) -> datetime | None:
        try:
            self.thread[-1].time
        except IndexError:
            return None

    @property
    def duration(self) -> timedelta | None:
        if self.start_time is None or self.end_time is None:
            return None
        return self.end_time - self.start_time

    @property
    def actors(self) -> list[str]:
        return list(set([m.sender for m in self.thread]))
