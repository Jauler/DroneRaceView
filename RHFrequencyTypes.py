from pydantic import BaseModel
from typing import Optional

class Frequency(BaseModel):
    band: Optional[str]
    channel: Optional[int]
    frequency: Optional[int]

class Frequencies(BaseModel):
    fdata: list[Frequency]
