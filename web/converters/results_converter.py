from RHTypes.RHPilotTypes import Pilots as RHPilots
from RHTypes.RHResultTypes import Results as RHResults
from RHTypes.RHFormatTypes import Formats as RHFormats
from RHTypes.RHClassTypes import Classes as RHClasses
from RHTypes.RHHeatTypes import Heats as RHHeats
from TemplateTypes import (
    Result as TResult,
    Results as TResults,
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
supported_result_converters = [
    ConsecutivesResultConverter,
    PointResultsConverter,
    EliminationsResultsConverter
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


