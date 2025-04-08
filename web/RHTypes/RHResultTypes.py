from pydantic import BaseModel
from typing import Optional



########################################
#
# result_data types
#
class LeaderboardResultSource(BaseModel):
    round: int
    heat: int
    displayname: str

class LeaderboardEntry(BaseModel):
    pilot_id: int
    callsign: str
    team_name: Optional[str]
    laps: int
    starts: int
    node: int
    total_time: str
    total_time_laps: str
    last_lap: Optional[str]
    average_lap: str
    fastest_lap: str
    consecutives: str
    consecutives_base: str
    consecutive_lap_start: Optional[int]
    fastest_lap_source: Optional[LeaderboardResultSource]
    consecutives_source: Optional[LeaderboardResultSource]
    total_time_raw: float
    total_time_laps_raw: float
    average_lap_raw: float
    fastest_lap_raw: float
    consecutives_raw: Optional[float]
    last_lap_raw: Optional[float]
    position: Optional[int]
    points: Optional[int]
    behind: Optional[int]

class LeaderboardMeta(BaseModel):
    primary_leaderboard: str
    win_condition: int
    team_racing_mode: bool
    start_behavior: int
    consecutives_count: int

class Leaderboard(BaseModel):
    by_race_time: list[LeaderboardEntry]
    by_fastest_lap: list[LeaderboardEntry]
    by_consecutives: list[LeaderboardEntry]
    meta: LeaderboardMeta

class Lap(BaseModel):
    id: int
    lap_time_stamp: float
    lap_time: float
    lap_time_formatted: str
    source: int
    deleted: bool

class Node(BaseModel):
    callsign: Optional[str]
    pilot_id: int
    node_index: int
    laps: list[Lap]

class Round(BaseModel):
    id: int
    start_time_formatted: Optional[str]
    nodes: list[Node]
    leaderboard: Optional[Leaderboard]

class Heat(BaseModel):
    heat_id: int
    displayname: str
    rounds: list[Round]
    leaderboard: Optional[Leaderboard]

class Class(BaseModel):
    id: int
    name: str
    description: str
    leaderboard: Optional[Leaderboard]
    ranking: Optional[bool]

class Results(BaseModel):
    heats: dict[str, Heat]
    heats_by_class: dict[str, list[int]]
    classes: dict[str, Class]
    event_leaderboard: Optional[Leaderboard]
    consecutives_count: int

########################################
#
# calss_data types
#

