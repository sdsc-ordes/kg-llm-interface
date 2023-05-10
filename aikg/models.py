from pydantic import BaseModel


class Conversation(BaseModel):
    last_message: str
    thread: str = ""
