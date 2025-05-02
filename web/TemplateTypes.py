from pydantic import BaseModel
from typing import Optional

# Pilot results info
class PilotResult(BaseModel):
    rank: int
    nickname: str
    pilot_id: int
    points: int
    fastest_lap: str
    fastest_lap_source: str
    consecutives_str: str
    consecutives_raw: float
    consecutives_base: int
    consecutives_source: str
    average_lap_time: str
    total_laps: int
    total_starts: int
    unfinished_races: int
    success_ratio: str
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


class PilotProgression(BaseModel):
    nickname: str
    points: list[int | None]

PilotsProgression = list[PilotProgression]


