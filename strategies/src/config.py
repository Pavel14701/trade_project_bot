from pydantic import BaseModel


class QuestConfig(BaseModel):
    url: str