from pydantic import BaseModel

class Class(BaseModel):
    id: int
    name: str
    displayname: str
    description: str
    format: int
    win_conditions: str | None = None
    rounds: int
    locked: bool

class Classes(BaseModel):
    classes: list[Class]

