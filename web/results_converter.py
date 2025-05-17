from mmap import ACCESS_DEFAULT
from RHTypes.RHHeatTypes import Heats as RHHeats
from RHTypes.RHPilotTypes import Pilots as RHPilots
from RHTypes.RHResultTypes import ByRaceTimeLeaderboardEntry, Leaderboard, LeaderboardEntry, LeaderboardMeta, Results as RHResults, LeaderboardResultSource
from RHTypes.RHFormatTypes import Formats as RHFormats
from RHTypes.RHClassTypes import Classes as RHClasses
from TemplateTypes import (
    PilotProgression as TPilotProgression,
    PilotsProgression as TPilotsProgression,
    PilotResult as TPilotResult,
    PointResults as TPointResults,
    ConsecutivesResults as TConsecutivesResults,
    Results as TResults,

)

from typing import Optional
from functools import cmp_to_key

BASE_POINTS = 1000

def insert_or_append(dictionary, key, element):
    if key in dictionary:
        dictionary[key].append(element)
    else:
        dictionary[key] = [element]

def format_fastest_lap_source(source: LeaderboardResultSource | None) -> str:
    if not source:
        return ""

    return f"({source.displayname} round {source.round})"

# A class which encapsulates conversion from RotorHazard data types,
# as collected by collector service, and converts it into TemplateTypes
# which are data types expected by front-end jinja templates for visualization
# ResultConverters may be of different types, depending on race format selected
# in RotorHazard itself.
class ResultConverter:
    @staticmethod
    def name() -> str:
        raise Exception("Not implemented")

    @staticmethod
    def convert(r: Optional[RHResults], p: RHPilots, c: list[int]) -> TConsecutivesResults | TPointResults:
        raise Exception("Not implemented")

# Consecutives result converter
#
# Ranks pilots according to best consecutives from all flights
class ConsecutivesResultConverter(ResultConverter):
    @staticmethod
    def name() -> str:
        return "consecutives"

    @staticmethod
    def format_milliseconds(ms):
        """Convert milliseconds to 'M:SS.sss' format"""
        total_seconds = ms / 1000
        minutes = int(total_seconds // 60)
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:06.3f}"

    @classmethod
    def cmp_lb_entries(cls, entry1: LeaderboardEntry, entry2: LeaderboardEntry):
        if entry1.consecutives_base != entry2.consecutives_base:
            return entry2.consecutives_base - entry1.consecutives_base

        if entry1.consecutives_raw and entry2.consecutives_raw:
            if entry1.consecutives_raw > entry2.consecutives_raw:
                return 1
            elif entry1.consecutives_raw < entry2.consecutives_raw:
                return -1

        if entry1.laps != entry2.laps:
            return entry2.laps - entry1.laps

        have_total_time_1 = entry1.total_time_raw and entry1.total_time_raw > 0.0
        have_total_time_2 = entry2.total_time_raw and entry2.total_time_raw > 0.0

        if have_total_time_1 and not have_total_time_2:
            return -1
        elif have_total_time_2 and not have_total_time_1:
            return 1
        elif have_total_time_1 and have_total_time_2:
            return entry1.total_time_raw - entry2.total_time_raw

        return 0

    @classmethod
    def merge_leaderboard_entries(cls, entry1: LeaderboardEntry, entry2: LeaderboardEntry) -> LeaderboardEntry:
        assert entry1.pilot_id == entry2.pilot_id, "pilot_id mismatch"
        assert entry1.callsign == entry2.callsign, "callsign mismatch"
        assert entry1.team_name == entry2.team_name, "team_name mismatch"

        total_laps = entry1.laps + entry2.laps
        total_time_raw = entry1.total_time_raw + entry2.total_time_raw
        total_time_laps_raw = entry1.total_time_laps_raw + entry2.total_time_laps_raw
        average_lap_raw = total_time_laps_raw / total_laps if total_laps else 0

        # --- Handle fastest lap ---
        f1_valid = entry1.fastest_lap_source is not None
        f2_valid = entry2.fastest_lap_source is not None
        if f1_valid and not f2_valid:
            fastest = entry1
        elif f2_valid and not f1_valid:
            fastest = entry2
        elif f1_valid and f2_valid:
            fastest = entry1 if entry1.fastest_lap_raw <= entry2.fastest_lap_raw else entry2
        else:
            fastest = None

        # --- Handle consecutives ---
        if entry1.consecutives_raw and not entry2.consecutives_raw:
            best = entry1
        elif entry2.consecutives_raw and not entry1.consecutives_raw:
            best = entry2
        elif entry1.consecutives_raw and entry2.consecutives_raw:
            if entry1.consecutives_base > entry2.consecutives_base:
                best = entry1
            elif entry1.consecutives_base < entry2.consecutives_base:
                best = entry2
            else:
                best = entry1 if entry1.consecutives_raw <= entry2.consecutives_raw else entry2
        else:
            best = None

        merged = LeaderboardEntry(
            pilot_id=entry1.pilot_id,
            callsign=entry1.callsign,
            team_name=entry1.team_name,
            laps=total_laps,
            starts=entry1.starts + entry2.starts,
            node=0,
            total_time_raw=total_time_raw,
            total_time_laps_raw=total_time_laps_raw,
            average_lap_raw=average_lap_raw,
            fastest_lap_raw=fastest.fastest_lap_raw if fastest else 0.0,
            fastest_lap=fastest.fastest_lap if fastest else "0:00.000",
            fastest_lap_source=fastest.fastest_lap_source if fastest else None,
            consecutives_raw=best.consecutives_raw if best else None,
            consecutives_base=best.consecutives_base if best else 0,
            consecutive_lap_start=best.consecutive_lap_start if best else None,
            consecutives_source=best.consecutives_source if best else None,
            last_lap="",
            last_lap_raw=0,
            total_time=cls.format_milliseconds(total_time_raw),
            total_time_laps=cls.format_milliseconds(total_time_laps_raw),
            average_lap=cls.format_milliseconds(average_lap_raw) if total_laps else "0:00.000",
            consecutives=cls.format_milliseconds(best.consecutives_raw) if best else "",
            position=None
        )

        return merged

    @classmethod
    def merge_leaderboards(cls, lb1: list[LeaderboardEntry], lb2: list[LeaderboardEntry]) -> list[LeaderboardEntry]:
        participants: dict[int, list[LeaderboardEntry]] = {}
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

    @classmethod
    def convert(cls, r: RHResults, p: RHPilots, c: list[int]) -> TConsecutivesResults:
        result = TConsecutivesResults(results=[])

        # Calculate merged consecutives leaderboard from all classes
        merged_lb: list[LeaderboardEntry] | None = None
        for rh_class in r.classes.values():
            # Skip classes with different display format
            if rh_class.id not in c:
                continue

            if rh_class.leaderboard:
                if not merged_lb:
                    merged_lb = rh_class.leaderboard.by_consecutives
                else:
                    merged_lb = cls.merge_leaderboards(
                            merged_lb,
                            rh_class.leaderboard.by_consecutives
                            )

        if merged_lb:
            for idx, entry in enumerate(merged_lb):
                result.results.append(TPilotResult(
                        rank = idx + 1,
                        nickname = entry.callsign,
                        pilot_id = entry.pilot_id,
                        points = 0,
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

# Points result converter
#
# Accumulates points across all flights having relevant race format
class PointResultsConverter(ConsecutivesResultConverter):
    @staticmethod
    def name() -> str:
        return "points"

    @classmethod
    def cmp_lb_entries(cls, entry1: ByRaceTimeLeaderboardEntry, entry2: ByRaceTimeLeaderboardEntry):
        if entry1.points and not entry2.points:
            return -1;
        elif entry2.points and not entry1.points:
            return 1
        elif entry1.points != entry2.points:
            assert entry1.points
            assert entry2.points
            return entry2.points - entry1.points

        return super().cmp_lb_entries(entry1, entry2)

    @classmethod
    def merge_leaderboard_entries(cls, entry1: ByRaceTimeLeaderboardEntry, entry2: ByRaceTimeLeaderboardEntry) -> ByRaceTimeLeaderboardEntry:
        merged_consecutives_entry = super().merge_leaderboard_entries(entry1, entry2)
        points = entry1.points if entry1.points else 0
        points += entry2.points if entry2.points else 0
        point_entry = ByRaceTimeLeaderboardEntry(**merged_consecutives_entry.dict(), points=points, behind=0)
        return point_entry


    # Used specifically with points type to display graph of all pilots
    @staticmethod
    def pilots_progression(r: RHResults, p: RHPilots, c: list[int]) -> TPilotsProgression:
        num_classes = len(r.classes) if r else 0

        # Initialize pilots points to 1000
        pilots_progression: dict[int, TPilotProgression] = {}
        pilot_points = {}
        for rh_pilot in p.pilots:
            pilots_progression[rh_pilot.pilot_id] = TPilotProgression(nickname=rh_pilot.callsign, points=[BASE_POINTS] + [None]*num_classes);
            pilot_points[rh_pilot.pilot_id] = BASE_POINTS

        # Add up points from each class leaderboard
        if r:
            for idx, class_id in enumerate(r.heats_by_class.keys()):
                if class_id not in c:
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

    @classmethod
    def convert(cls, r: RHResults, p: RHPilots, c: list[int]) -> TPointResults:

        pilots_progression = PointResultsConverter.pilots_progression(r, p, c)
        result = TPointResults(results=[], pilot_progression=pilots_progression)

        # Calculate merged consecutives leaderboard from all relevant classes
        merged_lb: list[ByRaceTimeLeaderboardEntry] | None = None
        for rh_class in r.classes.values():
            # Skip classes with different display format
            if rh_class.id not in c:
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
                        points = 0,
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

###########################################################
#
# List of all supported converters according to format name
#
supported_result_converters = [
    ConsecutivesResultConverter
]

# Convert RotorHazard data into relevant result types for fronted jinja templates
def results(r: Optional[RHResults], p: Optional[RHPilots], c: Optional[RHClasses], f: Optional[RHFormats]) -> TResults:
    results = TResults(results=[])

    # Do we have any inputs?
    if r is None or p is None or c is None or f is None:
        return results

    # Build a convenience map which will index our result converters (RH data -> TemplateTypes data)
    visible_format_ids = {}
    for rhformat in f.formats:
        for converter in supported_result_converters:
            format_str = f"display={converter.name()}"
            if format_str in rhformat.name:
                visible_format_ids[rhformat.id] = converter

    # Now build a list of classes per visible display format
    visible_classes = {}
    for rhclass in c.classes:
        if rhclass.format in visible_format_ids:
            insert_or_append(visible_classes, visible_format_ids[rhclass.format], rhclass.id)

    for converter, class_group in visible_classes.items():
        point_result = converter.convert(r, p, class_group)
        results.results.append(point_result)

    return results


