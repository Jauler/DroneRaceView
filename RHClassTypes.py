from pydantic import BaseModel
from typing import Optional

class Class(BaseModel):
    id: int
    name: str
    displayname: str
    description: str
    format: int
    win_conditions: Optional[str]
    rounds: int
    locked: bool

class Classes(BaseModel):
    classes: list[Class]

