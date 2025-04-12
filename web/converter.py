from RHTypes.RHRaceStatusTypes import RaceStatus
from RHTypes.RHHeatTypes import Heats as RHHeats
from RHTypes.RHPilotTypes import Pilots as RHPilots
from RHTypes.RHResultTypes import Results as RHResults, Ranking
from RHTypes.RHClassTypes import Classes as RHClasses
from RHTypes.RHFrequencyTypes import Frequencies as RHFrequencies, Frequency as RHFrequency
from TemplateTypes import (
    CurrentHeat as TCurrentHeat,
    CurrentHeatPilot as TCurrentHeatPilot,
    CurrentHeatPilots as TCurrentHeatPilots,
    PilotResults as TPilotResults,
    PilotResult as TPilotResult,
    Round as TRound,
    Rounds as TRounds,
    Heat as THeat,
    HeatPilot as THeatPilot
)

from typing import Optional

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

def current_heat(rc: Optional[RaceStatus], heats: Optional[RHHeats]) -> TCurrentHeat:
    if rc is None or heats is None:
        return "N/A"
    heat_id = rc.race_heat_id
    target = next((h for h in heats.heats if h.id == heat_id), None)
    if target is None:
        return NO_DATA
    return target.displayname

def current_pilots(rc: Optional[RaceStatus], h: Optional[RHHeats], p: Optional[RHPilots], f: Optional[RHFrequencies]) -> TCurrentHeatPilots:
    if rc is None or h is None or p is None or f is None:
        return []

    heat_id = rc.race_heat_id
    current_heat = next((h for h in h.heats if h.id == heat_id), None)
    if current_heat is None:
        return []

    slots = sorted(current_heat.slots, key=lambda s: s.node_index)
    pilot_ids = [s.pilot_id for s in slots]

    def find_pilot_by_id(pilot_id: int):
        assert p
        return next((p.callsign for p in p.pilots if p.pilot_id == pilot_id), "")

    return [TCurrentHeatPilot(
            nickname=find_pilot_by_id(pilot_id),
            channel = frequency_to_str(f.fdata[channel_id]))
            for channel_id, pilot_id in enumerate(pilot_ids) if len(f.fdata) > channel_id and f.fdata[channel_id].band is not None]

def pilot_results(r: Optional[RHResults], h: Optional[RHHeats], p: Optional[RHPilots]) -> TPilotResults:
    if p is None:
        return []

    pilot_results = {
            pilot.pilot_id:
            TPilotResult(
                rank = 1,
                nickname=pilot.callsign,
                points = BASE_POINTS,
                fastest_lap = NO_DATA,
                fastest_lap_source = NO_DATA,
                consecutives_str = NO_DATA,
                consecutives_raw = 0.0,
                consecutives_base = 0,
                consecutives_source = "",
                next_heat = NO_DATA,
                )
            for pilot in p.pilots
        }

    if r and r.event_leaderboard:
        # Fill in fastest_lap column
        for entry in r.event_leaderboard.by_fastest_lap:
            if entry.fastest_lap_source:
                time = entry.fastest_lap
                source = entry.fastest_lap_source.displayname
                pilot_results[entry.pilot_id].fastest_lap = f"{time} ({source})"
                pilot_results[entry.pilot_id].fastest_lap_source = source

        # Fill in consecutives column
        for entry in r.event_leaderboard.by_consecutives:
            if entry.consecutives_base and entry.consecutives_source and entry.consecutives_raw:
                source = entry.consecutives_source.displayname
                base = entry.consecutives_base
                time = entry.consecutives
                time_raw = entry.consecutives_raw
                pilot_results[entry.pilot_id].consecutives_str = f"{time} ({base} ) ({source})"
                pilot_results[entry.pilot_id].consecutives_base = base
                pilot_results[entry.pilot_id].consecutives_raw = time_raw
                pilot_results[entry.pilot_id].consecutives_source = source

            pilot_results[entry.pilot_id].consecutives_str = entry.consecutives
            if entry.consecutives_raw:
                pilot_results[entry.pilot_id].consecutives_raw = entry.consecutives_raw
            source = entry.consecutives_source.displayname if entry.consecutives_source else NO_DATA
            pilot_results[entry.pilot_id].consecutives_source = source

    # Fill in points column
    if r and r.classes:
        for c in r.classes.values():
            if isinstance(c.ranking, Ranking):
                for entry in c.ranking.ranking:
                    pilot_results[entry.pilot_id].points += entry.points

    # Fill in next_heat
    if h:
        all_heat_ids = set([h.id for h in h.heats])
        if not r:
            heats_with_leaderboard = set()
        else:
            heats_with_leaderboard = set([int(heat_id) for heat_id in r.heats.keys()])
        non_flown_heats = all_heat_ids - heats_with_leaderboard
        for non_flown_heat_id in sorted(list(non_flown_heats), reverse=True):
            heat = next((h for h in h.heats if h.id == non_flown_heat_id))
            assert heat is not None
            for slot in heat.slots:
                if slot.pilot_id == 0:
                    continue
                pilot_results[slot.pilot_id].next_heat = heat.displayname

    # Update rank. Keep the same amount of points - the same rank
    results = list(
            sorted(
                pilot_results.values(), key=lambda r: (
                    -r.points,
                    -r.consecutives_base,
                    r.consecutives_raw,
                    r.nickname
                )
            )
        )
    rank = 1
    for i, _ in enumerate(results):
        results[i].rank = rank
        if i+1 < len(results) and results[i+1].points != results[i].points:
            rank += 1

    return results


def rounds(r: Optional[RHResults], h: Optional[RHHeats], c: Optional[RHClasses], p: Optional[RHPilots], f: Optional[RHFrequencies]) -> TRounds:
    if c is None or h is None or p is None or f is None:
        return []

    def find_heats_by_class_id(class_id: int):
        assert h
        return [h for h in h.heats if h.class_id == class_id]
    def find_pilot_by_id(pilot_id: int):
        assert p
        return next((p for p in p.pilots if p.pilot_id == pilot_id), None)
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
            th = THeat(heat_name=rh_heat.displayname, pilots=[])
            for rh_slot in rh_heat.slots:
                if len(f.fdata) <= rh_slot.node_index or f.fdata[rh_slot.node_index].band is None:
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
                        channel=channel,
                        nickname=callsign,
                        position=position,
                        gains=gains,
                        points=points))

            race_round.heats.append(th)

        rounds.append(race_round)

    return rounds





