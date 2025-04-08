from pydantic import BaseModel

class Frequency(BaseModel):
    band: str | None = None
    channel: int | None = None
    frequency: int | None = None

class Frequencies(BaseModel):
    fdata: list[Frequency]
