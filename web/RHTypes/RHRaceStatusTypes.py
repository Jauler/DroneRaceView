from pydantic import BaseModel

class RaceStatus(BaseModel):
    race_status: int
    race_format_id: int
    race_heat_id: int
    race_class_id: int | None
    unlimited_time: int
    race_time_sec: int
    next_round: int
