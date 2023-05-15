from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid


class Message(BaseModel):
    text: str
    time: datetime
    sender: str
    triples: str | None = None


class Conversation(BaseModel):
    thread: list[Message]
    uid: str | None = str(uuid.uuid4())

    @property
    def start_time(self) -> datetime:
        return self.thread[0].time

    @property
    def end_time(self) -> datetime:
        return self.thread[-1].time

    @property
    def duration(self) -> timedelta:
        return self.end_time - self.start_time

    @property
    def actors(self) -> list[str]:
        return list(set([m.sender for m in self.thread]))
