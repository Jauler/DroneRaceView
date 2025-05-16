from pydantic import BaseModel

class PointsSettings(BaseModel):
    points_list: str | None = None

class Format(BaseModel):
    id: int
    name: str
    unlimited_time: int
    race_time_sec: int
    lap_grace_sec: int
    staging_fixed_tones: int
    staging_delay_tones: int
    start_delay_min: int
    start_delay_max: int
    number_laps_win: int
    win_condition: int
    team_racing_mode: int
    start_behavior: int
    locked: bool
    points_method: str | None = None
    points_settings: PointsSettings | None = None

class Formats(BaseModel):
    formats: list[Format]
