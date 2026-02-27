from pydantic import BaseModel # type: ignore


class QuestConfig(BaseModel):
    url: str