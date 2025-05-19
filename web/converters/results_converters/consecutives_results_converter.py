from typing import Optional
from functools import cmp_to_key

from RHTypes.RHPilotTypes import Pilots as RHPilots
from RHTypes.RHResultTypes import LeaderboardEntry, Results as RHResults, LeaderboardResultSource
from TemplateTypes import (
    ConsecutivesResults as TConsecutivesResults,
    PilotResult as TPilotResult
)

from converters.results_converters.results_converter_types import ResultConverter


def insert_or_append(dictionary, key, element):
    if key in dictionary:
        dictionary[key].append(element)
    else:
        dictionary[key] = [element]

def format_fastest_lap_source(source: LeaderboardResultSource | None) -> str:
    if not source:
        return ""

    return f"({source.displayname} round {source.round})"

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
    def convert(cls,
            r: Optional[RHResults],
            _p,
            _c,
            _h,
            relevant_classes: list[int]) -> TConsecutivesResults:
        result = TConsecutivesResults(results=[])

        if not r:
            return result

        # Calculate merged consecutives leaderboard from all classes
        merged_lb: list[LeaderboardEntry] | None = None
        for rh_class in r.classes.values():
            # Skip classes with different display format
            if rh_class.id not in relevant_classes:
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


