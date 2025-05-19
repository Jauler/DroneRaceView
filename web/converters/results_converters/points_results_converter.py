from typing import Optional
from functools import cmp_to_key

from converters.results_converters.consecutives_results_converter import ConsecutivesResultConverter
from converters.results_converters.consecutives_results_converter import format_fastest_lap_source
from converters.results_converters.results_converter_types import insert_or_append

from RHTypes.RHResultTypes import ByRaceTimeLeaderboardEntry, Results as RHResults
from RHTypes.RHPilotTypes import Pilots as RHPilots

from TemplateTypes import (
        PilotProgression as TPilotProgression,
        PilotsProgression as TPilotsProgression,
        PointResults as TPointResults,
        PilotResult as TPilotResult
)

BASE_POINTS = 1000

# Points result converter
#
# Accumulates points across all flights having relevant race format
class PointResultsConverter(ConsecutivesResultConverter):
    @staticmethod
    def name() -> str:
        return "points"

    @classmethod
    def cmp_lb_entries(cls, entry1: ByRaceTimeLeaderboardEntry, entry2: ByRaceTimeLeaderboardEntry):
        entry1_has_points = entry1.points is not None
        entry2_has_points = entry2.points is not None
        if entry1_has_points and not entry2_has_points:
            return -1;
        elif entry2_has_points and not entry1_has_points:
            return 1
        elif entry1.points != entry2.points:
            assert entry1.points is not None
            assert entry2.points is not None
            return entry2.points - entry1.points

        return super().cmp_lb_entries(entry1, entry2)

    @classmethod
    def merge_leaderboard_entries(cls, entry1: ByRaceTimeLeaderboardEntry, entry2: ByRaceTimeLeaderboardEntry) -> ByRaceTimeLeaderboardEntry:
        merged_consecutives_entry = super().merge_leaderboard_entries(entry1, entry2)
        points = (entry1.points if entry1.points is not None else 0) + (entry2.points if entry2.points is not None else 0)
        point_entry = ByRaceTimeLeaderboardEntry(**merged_consecutives_entry.dict(), points=0, behind=0)
        point_entry.points = points
        return point_entry

    @classmethod
    def merge_leaderboards(cls, lb1: list[ByRaceTimeLeaderboardEntry], lb2: list[ByRaceTimeLeaderboardEntry]) -> list[ByRaceTimeLeaderboardEntry]:
        participants: dict[int, list[ByRaceTimeLeaderboardEntry]] = {}
        for entry in lb1:
            insert_or_append(participants, entry.pilot_id, entry)
        for entry in lb2:
            insert_or_append(participants, entry.pilot_id, entry)

        for pilot_id, lb_entries in participants.items():
            if len(lb_entries) <= 1:
                continue

            participants[pilot_id] = [cls.merge_leaderboard_entries(lb_entries[0], lb_entries[1])]

        results = [v[0] for v in participants.values()]
        return sorted(results, key=cmp_to_key(cls.cmp_lb_entries))


    # Used specifically with points type to display graph of all pilots
    @staticmethod
    def pilots_progression(r: RHResults, p: RHPilots, relevant_classes: list[int]) -> TPilotsProgression:
        num_classes = 0
        for rh_class_id in r.classes:
            if int(rh_class_id) in relevant_classes:
                num_classes += 1

        # Initialize pilots points to 1000
        pilots_progression: dict[int, TPilotProgression] = {}
        pilot_points = {}
        for rh_pilot in p.pilots:
            pilots_progression[rh_pilot.pilot_id] = TPilotProgression(nickname=rh_pilot.callsign, points=[BASE_POINTS] + [None]*num_classes);
            pilot_points[rh_pilot.pilot_id] = BASE_POINTS

        # Add up points from each class leaderboard
        if r:
            for idx, class_id in enumerate(r.heats_by_class.keys()):
                if int(class_id) not in relevant_classes:
                    continue

                heats_in_class = r.heats_by_class[class_id]
                for heat_id in heats_in_class:
                    if str(heat_id) not in r.heats:
                        continue
                    rh_heat = r.heats[str(heat_id)]
                    if not rh_heat.leaderboard:
                        continue
                    for entry in rh_heat.leaderboard.by_race_time:
                        pilot_id = entry.pilot_id
                        gains = entry.points if entry.points else 0
                        points_before_round = pilot_points[entry.pilot_id]
                        points_after_round = points_before_round + gains

                        pilots_progression[pilot_id].points[idx] = points_after_round
                        pilot_points[pilot_id] = points_after_round

        return list(pilots_progression.values())

    @classmethod
    def convert(cls,
            r: Optional[RHResults],
            p: Optional[RHPilots],
            _c,
            _h,
            relevant_classes: list[int]) -> TPointResults:
        result = TPointResults(results=[], pilots_progression=[])

        if not r or not p:
            return result

        result.pilots_progression = PointResultsConverter.pilots_progression(r, p, relevant_classes)

        if not r:
            return result

        # Calculate merged consecutives leaderboard from all relevant classes
        merged_lb: list[ByRaceTimeLeaderboardEntry] | None = None
        for rh_class in r.classes.values():
            # Skip classes with different display format
            if rh_class.id not in relevant_classes:
                continue

            if rh_class.leaderboard:
                if not merged_lb:
                    merged_lb = rh_class.leaderboard.by_race_time
                else:
                    merged_lb = cls.merge_leaderboards(
                            merged_lb,
                            rh_class.leaderboard.by_race_time
                            )

        if merged_lb:
            for idx, entry in enumerate(merged_lb):
                result.results.append(TPilotResult(
                        rank = idx + 1,
                        nickname = entry.callsign,
                        pilot_id = entry.pilot_id,
                        points = BASE_POINTS + (entry.points if entry.points else 0),
                        fastest_lap=entry.fastest_lap,
                        fastest_lap_source=format_fastest_lap_source(entry.fastest_lap_source),
                        consecutives_str=entry.consecutives,
                        consecutives_raw=entry.consecutives_raw if entry.consecutives_raw else 0.0,
                        consecutives_base=entry.consecutives_base,
                        consecutives_source=format_fastest_lap_source(entry.consecutives_source),
                        average_lap_time=entry.average_lap,
                        total_laps=entry.laps,
                        total_starts=entry.starts,
                        unfinished_races=0,
                        success_ratio="",
                        next_heat=None,
                    ))

        return result


