from pydantic import BaseModel



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
    team_name: str | None = None
    laps: int
    starts: int
    node: int
    total_time: str
    total_time_laps: str
    last_lap: str | None = None
    average_lap: str
    fastest_lap: str
    consecutives: str
    consecutives_base: int
    consecutive_lap_start: int | None = None
    fastest_lap_source: LeaderboardResultSource | None = None
    consecutives_source: LeaderboardResultSource | None = None
    total_time_raw: float
    total_time_laps_raw: float
    average_lap_raw: float
    fastest_lap_raw: float
    consecutives_raw: float | None = None
    last_lap_raw: float | None = None
    position: int | None = None

class ByRaceTimeLeaderboardEntry(LeaderboardEntry):
    points: int | None = None
    behind: int

class LeaderboardMeta(BaseModel):
    primary_leaderboard: str
    win_condition: int | None
    team_racing_mode: bool
    start_behavior: int | None
    consecutives_count: int

class Leaderboard(BaseModel):
    by_race_time: list[ByRaceTimeLeaderboardEntry]
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
    callsign: str | None = None
    pilot_id: int
    node_index: int
    laps: list[Lap]

class Round(BaseModel):
    id: int
    start_time_formatted: str | None = None
    nodes: list[Node]
    leaderboard: Leaderboard | None = None

class Heat(BaseModel):
    heat_id: int
    displayname: str
    rounds: list[Round]
    leaderboard: Leaderboard | None = None

class RankingEntry(BaseModel):
    pilot_id: int
    callsign: str
    team_name: str
    points: int
    position: int

class Ranking(BaseModel):
    ranking: list[RankingEntry]

class Class(BaseModel):
    id: int
    name: str
    description: str
    leaderboard: Leaderboard | None = None
    ranking: Ranking | bool | None = None

class Results(BaseModel):
    heats: dict[str, Heat]
    heats_by_class: dict[str, list[int]]
    classes: dict[str, Class]
    event_leaderboard: Leaderboard | None = None
    consecutives_count: int

########################################
#
# calss_data types
#

