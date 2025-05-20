from typing import Optional

from RHTypes.RHResultTypes import Leaderboard, Results as RHResults
from RHTypes.RHHeatTypes import Heats as RHHeats
from RHTypes.RHPilotTypes import Pilots as RHPilots
from RHTypes.RHClassTypes import Classes as RHClasses
from TemplateTypes import (
    FinalsResults as TFinalsResults,
    FinalsResult as TFinalsResult,
    FinalsFinalist as TFinalsFinalist,
)

import json

from converters.results_converters.results_converter_types import ResultConverter

# Consecutives result converter
#
# Ranks pilots according to best consecutives from all flights
class FinalsResultConverter(ResultConverter):
    @staticmethod
    def name() -> str:
        return "finals"

    @classmethod
    def convert(cls,
            r: Optional[RHResults],
            p: Optional[RHPilots],
            c: Optional[RHClasses],
            h: Optional[RHHeats],
            relevant_classes: list[int]) -> TFinalsResults:
        results = TFinalsResults(results=[])
        if not r or not h or not p or not c:
            return results

        def pilot_callsign_by_id(pilot_id) -> str:
            assert p
            pilot = next((pilot for pilot in p.pilots if pilot.pilot_id == pilot_id), None)
            if not pilot:
                return ""
            return pilot.callsign
        def class_name_by_heat_id(class_id) -> str:
            assert c
            rh_class = next((rh_class for rh_class in c.classes if rh_class.id == class_id), None)
            if not rh_class:
                return ""
            return rh_class.displayname
        def lb_by_heat_id(heat_id) -> Leaderboard | None:
            assert r
            heat = next((heat for heat in r.heats.values() if heat.heat_id == heat_id), None)
            if not heat:
                return None
            return heat.leaderboard

        for relevant_class_id in relevant_classes:
            positions_by_pilot: dict[int, TFinalsFinalist] = {}
            for heat in h.heats:
                # Filter out non-finals classes
                if heat.class_id != relevant_class_id:
                    continue

                # Prepopulate pilot list from first heat in class
                # Other heats should have the same pilots
                for slot in heat.slots:
                    if slot.pilot_id == 0:
                        continue
                    if slot.pilot_id in positions_by_pilot:
                        continue
                    positions_by_pilot[slot.pilot_id] = TFinalsFinalist(
                            callsign=pilot_callsign_by_id(slot.pilot_id),
                            race_positions=[],
                            totals=0
                        )

                lb = lb_by_heat_id(heat.id)
                if not lb:
                    continue


                for lb_entry in lb.by_race_time:
                    if lb_entry.pilot_id not in positions_by_pilot:
                        continue
                    positions_by_pilot[lb_entry.pilot_id].callsign = lb_entry.callsign
                    positions_by_pilot[lb_entry.pilot_id].race_positions.append(lb_entry.position)

            # Update totals
            for pilot_id, finalists in positions_by_pilot.items():
                total = 0
                for race_position in finalists.race_positions:
                    if race_position:
                        total += race_position
                positions_by_pilot[pilot_id].totals = total

            # Get max race count
            race_count = max((len(p.race_positions) for p in positions_by_pilot.values()), default = 1)
            if race_count <= 0:
                race_count = 1

            # get class name
            class_name = class_name_by_heat_id(int(relevant_class_id))

            # Finally append FinalsResult
            results.results.append(TFinalsResult(
                displayname=class_name,
                race_count=race_count,
                finalists=list(positions_by_pilot.values())
            ))


        return results


