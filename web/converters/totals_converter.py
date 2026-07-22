from typing import Optional

from RHTypes.RHResultTypes import LeaderboardEntry, Results as RHResults
from TemplateTypes import (
    Totals as TTotals,
    TotalsEntry as TTotalsEntry,
)

from converters.results_converters.consecutives_results_converter import format_fastest_lap_source


def _entry(idx: int, e: LeaderboardEntry) -> TTotalsEntry:
    return TTotalsEntry(
        rank=idx + 1,
        nickname=e.callsign,
        pilot_id=e.pilot_id,
        laps=e.laps,
        total_time=e.total_time,
        fastest_lap=e.fastest_lap,
        fastest_lap_source=format_fastest_lap_source(e.fastest_lap_source),
        consecutives_base=e.consecutives_base,
        consecutives_str=e.consecutives,
        consecutives_source=format_fastest_lap_source(e.consecutives_source),
    )


def _entries(lb: list[LeaderboardEntry]) -> list[TTotalsEntry]:
    return [_entry(idx, e) for idx, e in enumerate(lb)]


# Convert whole-event leaderboard into totals view type.
#
# Each list is already sorted by RotorHazard, so rank is simply the
# position in the list. This view is format-agnostic (no points).
def totals(r: Optional[RHResults]) -> Optional[TTotals]:
    if r is None or r.event_leaderboard is None:
        return None

    el = r.event_leaderboard
    return TTotals(
        by_consecutives=_entries(el.by_consecutives),
        by_fastest_lap=_entries(el.by_fastest_lap),
        by_race_time=_entries(el.by_race_time),
    )
