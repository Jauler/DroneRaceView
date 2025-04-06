from pydantic import BaseModel
from typing import Optional

class HeatSlot(BaseModel):
    id: int
    node_index: int
    pilot_id: int
    method: int

class Heat(BaseModel):
    id: int
    displayname: str
    name: Optional[str]
    auto_name: Optional[str]
    class_id: int
    group_id: int
    status: int
    auto_frequency: bool
    active: bool
    next_round: int
    slots: list[HeatSlot]
    locked: bool

class Heats(BaseModel):
    heats: list[Heat]
