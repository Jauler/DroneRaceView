from pydantic import BaseModel

class HeatSlot(BaseModel):
    id: int
    node_index: int | None = None
    pilot_id: int
    method: int

class Heat(BaseModel):
    id: int
    displayname: str
    name: str | None = None
    auto_name: str | None = None
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
