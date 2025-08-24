from RHTypes.RHHeatTypes import Heats as RHHeats
from RHTypes.RHPilotTypes import Pilots as RHPilots
from RHTypes.RHResultTypes import Results as RHResults, Ranking
from TemplateTypes import (
    PilotResults as TPilotResults,
    PilotResult as TPilotResult,
    PilotRound as TPilotRound,
    PilotRounds as TPilotRounds
)

from typing import Optional

NO_DATA = "N/A"
EMPTY = ""
BASE_POINTS = 1000

def pilot_results(r: Optional[RHResults], h: Optional[RHHeats], p: Optional[RHPilots]) -> TPilotResults:
    if p is None:
        return []

    pilot_results = {
            pilot.pilot_id:
            TPilotResult(
                rank = 1,
                pilot_id = pilot.pilot_id,
                nickname=pilot.callsign,
                points = BASE_POINTS,
                fastest_lap = NO_DATA,
                fastest_lap_source = NO_DATA,
                consecutives_str = NO_DATA,
                consecutives_raw = 0.0,
                consecutives_base = 0,
                consecutives_source = "",
                average_lap_time = NO_DATA,
                total_laps = 0,
                total_starts = 0,
                unfinished_races = 0,
                success_ratio = NO_DATA,
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
                race_round = entry.fastest_lap_source.round
                pilot_results[entry.pilot_id].fastest_lap = f"{time} ({source} round {race_round})"
                pilot_results[entry.pilot_id].fastest_lap_source = source

        # Fill in consecutives column
        for entry in r.event_leaderboard.by_consecutives:
            if entry.consecutives_base and entry.consecutives_source and entry.consecutives_raw:
                source = entry.consecutives_source.displayname
                race_round = entry.consecutives_source.round
                base = entry.consecutives_base
                time = entry.consecutives
                time_raw = entry.consecutives_raw
                pilot_results[entry.pilot_id].consecutives_str = f"{base}/{time} ({source} round {race_round})"
                pilot_results[entry.pilot_id].consecutives_base = base
                pilot_results[entry.pilot_id].consecutives_raw = time_raw
                pilot_results[entry.pilot_id].consecutives_source = source

        # Fill some race totals
        for entry in r.event_leaderboard.by_race_time:
            pilot_results[entry.pilot_id].average_lap_time = entry.average_lap
            pilot_results[entry.pilot_id].total_starts = entry.starts
            pilot_results[entry.pilot_id].total_laps = entry.laps

        # Count finished races
        consecutive_base = r.consecutives_count
        for heat in r.heats.values():
            for race_round in heat.rounds:
                for race_round_node in race_round.nodes:
                    pilot_id = race_round_node.pilot_id

                    laps_count = 0
                    for lap in race_round_node.laps:
                        if lap.deleted:
                            continue
                        laps_count += 1

                    if 0 < laps_count and laps_count <= consecutive_base and pilot_id in pilot_results:
                        pilot_results[pilot_id].unfinished_races += 1

        # Populate success ratio
        for pilot_id in pilot_results.keys():
            attempt_count = pilot_results[pilot_id].total_starts
            fail_count = pilot_results[pilot_id].unfinished_races
            if attempt_count > 0:
               pilot_results[pilot_id].success_ratio = str(round((attempt_count - fail_count) / attempt_count * 100))

    # Fill in points column
    if r and r.classes:
        for c in r.classes.values():
            if isinstance(c.ranking, Ranking):
                for entry in c.ranking.ranking:
                    if entry.points is not None:
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

def pilot_result(r: Optional[RHResults], h: Optional[RHHeats], p: Optional[RHPilots], pilot_id) -> TPilotResult:
    pilots = pilot_results(r, h, p)
    for pilot in pilots:
        if pilot.pilot_id == pilot_id:
            return pilot

    return TPilotResult(
        rank = 1,
        pilot_id = pilot_id,
        nickname="",
        points = BASE_POINTS,
        fastest_lap = NO_DATA,
        fastest_lap_source = NO_DATA,
        consecutives_str = NO_DATA,
        consecutives_raw = 0.0,
        consecutives_base = 0,
        consecutives_source = "",
        average_lap_time = NO_DATA,
        total_laps = 0,
        total_starts = 0,
        unfinished_races = 0,
        success_ratio = NO_DATA,
        next_heat = NO_DATA,
    )

def pilot_lap_times(r: Optional[RHResults], pilot_id: int) -> list[float]:
    if not r:
        return []

    lap_times = []
    for heat in r.heats.values():
        for race_round in heat.rounds:
            for seat in race_round.nodes:
                if seat.pilot_id != pilot_id:
                    continue
                is_holeshot = True
                for lap in seat.laps:
                    if lap.deleted:
                        continue

                    # It would be wiser to take a look
                    # At StartingBehavior, but its a bit overkill.
                    # Lets just assume, that first lap is holeshot always
                    if is_holeshot:
                        is_holeshot = False
                        continue

                    lap_times.append(round(lap.lap_time / 1000, 3))

    return lap_times


def pilot_rounds(r: Optional[RHResults], h: Optional[RHHeats], pilot_id: int) -> TPilotRounds:
    if not r or not h:
        return []

    consecutives_base = r.consecutives_count
    pilot_rounds = []
    for heat in r.heats.values():
        for race_round_idx, race_round in enumerate(heat.rounds):
            for seat in race_round.nodes:
                if seat.pilot_id != pilot_id:
                    continue

                # fill in laps
                laps = []
                started = False
                for idx, lap in enumerate(seat.laps):
                    if lap.deleted:
                        continue

                    started = True

                    # skip holeshot
                    if idx == 0:
                        continue

                    laps.append(round(lap.lap_time / 1000, 3))

                # determine status
                if not started:
                    status = "skipped"
                elif len(laps) < consecutives_base:
                    status = "crashed"
                else:
                    status = "finished"

                # Determine position
                position = None
                lb = race_round.leaderboard.by_race_time if race_round.leaderboard else []
                for entry in lb:
                    if entry.pilot_id == pilot_id and entry.position:
                        position = str(entry.position)

                # Determine round name
                round_name = ""
                for db_heat in h.heats:
                    if db_heat.id != heat.heat_id:
                        continue
                    round_name = f"{db_heat.displayname} round {race_round_idx + 1}"


                pilot_rounds.append(TPilotRound(
                    round_name=round_name,
                    status = status,
                    position = position,
                    laps = laps
                ))

    return pilot_rounds
