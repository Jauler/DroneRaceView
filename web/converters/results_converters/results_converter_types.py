from typing import Optional

from RHTypes.RHPilotTypes import Pilots as RHPilots
from RHTypes.RHResultTypes import Results as RHResults
from RHTypes.RHClassTypes import Classes as RHClasses
from RHTypes.RHHeatTypes import Heats as RHHeats

from TemplateTypes import (
        ConsecutivesResults as TConsecutivesResults,
        PointResults as TPointResults,
        EliminationResults as TEliminationResults,
)

def insert_or_append(dictionary, key, element):
    if key in dictionary:
        dictionary[key].append(element)
    else:
        dictionary[key] = [element]


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
    def convert(
            r: Optional[RHResults],
            p: Optional[RHPilots],
            c: Optional[RHClasses],
            h: Optional[RHHeats],
            relevant_classes: list[int]) -> TConsecutivesResults | TPointResults | TEliminationResults:
        raise Exception("Not implemented")


