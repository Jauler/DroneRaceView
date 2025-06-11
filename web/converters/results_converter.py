from RHTypes.RHPilotTypes import Pilots as RHPilots
from RHTypes.RHResultTypes import Results as RHResults, Ranking as RHRanking
from RHTypes.RHFormatTypes import Formats as RHFormats
from RHTypes.RHClassTypes import Classes as RHClasses
from RHTypes.RHHeatTypes import Heats as RHHeats
from TemplateTypes import (
    Result as TResult,
    Results as TResults,
    RankingEntry as TRankingEntry,
    Ranking as TRanking,
)

from typing import Optional

from converters.results_converters.results_converter_types import insert_or_append

###########################################################
#
# List of all supported converters according to format name
#
from converters.results_converters.consecutives_results_converter import ConsecutivesResultConverter
from converters.results_converters.points_results_converter import PointResultsConverter
from converters.results_converters.eliminations_results_converter import EliminationsResultsConverter
from converters.results_converters.finals_results_converter import FinalsResultConverter
from converters.results_converters.pointfinals_results_converter import PointFinalsResultsConverter
supported_result_converters = [
    ConsecutivesResultConverter,
    PointResultsConverter,
    EliminationsResultsConverter,
    PointFinalsResultsConverter,
    FinalsResultConverter
]

# Convert RotorHazard data into relevant result types for fronted jinja templates
def results(r: Optional[RHResults],
            p: Optional[RHPilots],
            c: Optional[RHClasses],
            h: Optional[RHHeats],
            f: Optional[RHFormats]) -> TResults:
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
        result = TResult(
                result_type=converter.name(),
                data=converter.convert(r, p, c, h, class_group)
                )
        results.results.append(result)

    return results

def ranking(r: Optional[RHResults],
            p: Optional[RHPilots],
            c: Optional[RHClasses],
            h: Optional[RHHeats],
            f: Optional[RHFormats]) -> TRanking | None:
    ranking_entries = []

    # Do we have any inputs?
    if r is None or p is None or c is None or f is None:
        return None

    # Build a convenience map which will index our result converters (RH data -> TemplateTypes data)
    visible_format_ids = set()
    for rhformat in f.formats:
        format_str = f"final_ranking=true"
        if format_str in rhformat.name:
            visible_format_ids.add(rhformat.id)

    # Now build a list of classes per visible display format
    for rhclass in c.classes:
        if rhclass.format not in visible_format_ids:
            continue

        if str(rhclass.id) not in r.classes:
            continue

        ranked_class = r.classes[str(rhclass.id)]

        if not isinstance(ranked_class.ranking, RHRanking):
            continue

        for rank_entry in ranked_class.ranking.ranking:
            ranking_entries.append(
                    TRankingEntry(
                        rank = rank_entry.position,
                        nickname = rank_entry.callsign,
                        pilot_id = rank_entry.pilot_id))

    if len(ranking_entries) <= 0:
        return None

    return TRanking(ranking=ranking_entries)


