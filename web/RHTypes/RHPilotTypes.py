from pydantic import BaseModel
from typing import Optional

class Pilot(BaseModel):
    pilot_id: int
    callsign: str
    team: str
    phonetic: str
    active: bool
    team_options: str
    color: str
    locked: bool

class Pilots(BaseModel):
    pilots: list[Pilot]

