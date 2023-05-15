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
