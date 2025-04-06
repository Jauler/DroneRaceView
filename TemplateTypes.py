from pydantic import BaseModel
from typing import Optional

# Pilot results info
class PilotResult(BaseModel):
    rank: int
    nickname: str
    points: int
    fastest_lap: str
    fastest_lap_source: str
    fastest_3_laps: str
    fastest_3_laps_source: str
    next_heat: Optional[str]

PilotResults = list[PilotResult]

# Current heat info
class CurrentHeatPilot(BaseModel):
    nickname: str
    channel: str

CurrentHeat = str
CurrentHeatPilots = list[CurrentHeatPilot]

# Heats info
class HeatPilot(BaseModel):
    channel: str
    nickname: str
    position: str
    gains: str
    points: str

class Heat(BaseModel):
    heat_name: str
    pilots: list[HeatPilot]

class Round(BaseModel):
    round_name: str
    heats: list[Heat]

Rounds = list[Round]


