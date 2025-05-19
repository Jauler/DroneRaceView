from typing import Optional
from RHTypes.RHResultTypes import Results as RHResults, Ranking
from RHTypes.RHHeatTypes import Heats as RHHeats
from RHTypes.RHClassTypes import Classes as RHClasses
from RHTypes.RHPilotTypes import Pilots as RHPilots
from RHTypes.RHFrequencyTypes import Frequencies as RHFrequencies, Frequency as RHFrequency

from TemplateTypes import (
    Rounds as TRounds,
    Round as TRound,
    Heat as THeat,
    HeatPilot as THeatPilot
)

NO_DATA = "N/A"
EMPTY = ""
BASE_POINTS = 1000


def frequency_to_str(f: RHFrequency):
    return f"{f.band}{f.channel} ({f.frequency} Mhz)"

def value_or_default(v, d):
    if v is not None:
        return v
    else:
        return d

def map_or_default(m, v, d):
    if v is None:
        return d

    if v not in m:
        return d

    return m[v]

def rounds(r: Optional[RHResults], h: Optional[RHHeats], c: Optional[RHClasses], p: Optional[RHPilots], f: Optional[RHFrequencies]) -> TRounds:
    if c is None or h is None or p is None or f is None:
        return []

    def find_heats_by_class_id(class_id: int):
        assert h
        return [h for h in h.heats if h.class_id == class_id]
    def find_pilot_by_id(pilot_id: int):
        assert p
        return next((p for p in p.pilots if p.pilot_id == pilot_id), None)
    def is_heat_completed(heat_id: int):
        if not r or str(heat_id) not in r.heats:
            return False
        if r.heats[str(heat_id)].leaderboard is None:
            return False
        return True
    def find_pilot_leaderboard_by_heat_and_pilot_id(heat_id: int, pilot_id: int):
        if not r or str(heat_id) not in r.heats:
            return None
        leaderboard = r.heats[str(heat_id)].leaderboard
        if leaderboard is None:
            return None
        for entry in leaderboard.by_race_time:
            if entry.pilot_id != pilot_id:
                continue
            return entry
        return None
    def find_gains_for_pilot_in_class(class_id, pilot_id):
        if r and str(class_id) in r.classes:
            ranking = r.classes[str(class_id)].ranking
            if isinstance(ranking, Ranking):
                return next((p.points for p in ranking.ranking if p.pilot_id == pilot_id), None)
        return None

    # Initialize pilots points to 1000
    pilot_points = {}
    for rh_pilot in p.pilots:
        pilot_points[rh_pilot.pilot_id] = BASE_POINTS;

    rounds = []
    for race_class in c.classes:
        race_round = TRound(round_name=race_class.displayname, heats=[])
        rh_heats = find_heats_by_class_id(race_class.id)
        for rh_heat in rh_heats:
            th = THeat(heat_name=rh_heat.displayname, pilots=[], completed=is_heat_completed(rh_heat.id))
            for rh_slot in rh_heat.slots:
                # Validate data
                if rh_slot.node_index is None:
                    continue
                if len(f.fdata) <= rh_slot.node_index:
                    continue
                if f.fdata[rh_slot.node_index].band is None:
                    continue

                rhp = find_pilot_by_id(rh_slot.pilot_id)

                # pilot info
                channel = frequency_to_str(f.fdata[rh_slot.node_index])
                callsign = value_or_default(rhp.callsign, EMPTY) if rhp is not None else EMPTY

                # result info
                lb_entry = find_pilot_leaderboard_by_heat_and_pilot_id(rh_heat.id, rh_slot.pilot_id)
                if lb_entry is not None and rhp is not None:
                    position = str(value_or_default(lb_entry.position, NO_DATA))

                    # Get gains from results
                    gains = find_gains_for_pilot_in_class(race_class.id, rh_slot.pilot_id)

                    if gains is None:
                        points = NO_DATA
                        gains = NO_DATA
                    else:
                        pilot_points[rh_slot.pilot_id] += gains
                        points = str(pilot_points[rh_slot.pilot_id])
                        gains = str(gains)

                else:
                    position = NO_DATA
                    gains = NO_DATA
                    points = NO_DATA

                th.pilots.append(THeatPilot(
                        pilot_id=rh_slot.pilot_id if rh_slot.pilot_id > 0 else None,
                        channel=channel,
                        nickname=callsign,
                        position=position,
                        gains=gains,
                        points=points))

            race_round.heats.append(th)

        rounds.append(race_round)

    rounds.reverse()

    return rounds

