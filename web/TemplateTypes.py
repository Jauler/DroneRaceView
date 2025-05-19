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

class PilotProgression(BaseModel):
    nickname: str
    points: list[int | None]

PilotsProgression = list[PilotProgression]

class ConsecutivesResults(BaseModel):
    results: PilotResults

class PointResults(BaseModel):
    results: PilotResults
    pilots_progression: PilotsProgression

# Heats info
class HeatPilot(BaseModel):
    pilot_id: Optional[int]
    channel: str
    nickname: str
    position: str
    gains: str
    points: str

class Heat(BaseModel):
    heat_name: str
    completed: bool
    pilots: list[HeatPilot]

class Round(BaseModel):
    round_name: str
    heats: list[Heat]

Rounds = list[Round]

class PilotRound(BaseModel):
    round_name: str
    status: str
    position: str | None
    laps: list[float]

PilotRounds = list[PilotRound]



# Elimination bracket info
class EliminationStage(BaseModel):
    id: int
    name: str
    type: str
    settings: dict

class EliminationGroup(BaseModel):
    id: int
    stage_id: int
    number: int

class EliminationParticipant(BaseModel):
    id: int
    name: str

class EliminationRound(BaseModel):
    id: int
    number: int
    stage_id: int
    group_id: int

class EliminationOpponent(BaseModel):
    id: int

class EliminationMatch(BaseModel):
    id: int
    number: int
    stage_id: int
    group_id: int
    round_id: int
    child_count: int
    status: int
    previous_connection_type: str | bool | None
    next_connection_type: str | bool | None
    opponent1: EliminationOpponent | None
    opponent2: EliminationOpponent | None
    opponent3: EliminationOpponent | None
    opponent4: EliminationOpponent | None

class EliminationTrack(BaseModel):
    stage: list[EliminationStage]
    group: list[EliminationGroup]
    participant: list[EliminationParticipant]
    round: list[EliminationRound]
    match: list[EliminationMatch]
    match_game: list

class EliminationResults(BaseModel):
    track: dict[str, EliminationTrack]

class EliminationRoundMeta(BaseModel):
    number:int
    track: str
    displayname: str
    previous_connection_type: str | bool | None
    next_connection_type: str | bool | None

class Result(BaseModel):
    result_type: str # One of "points | consecutives | ..."
    data: PointResults | ConsecutivesResults | EliminationResults

class Results(BaseModel):
    results: list[Result]




