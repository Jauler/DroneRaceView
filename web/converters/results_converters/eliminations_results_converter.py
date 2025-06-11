from typing import Optional
from natsort import natsorted

from RHTypes.RHHeatTypes import Heats as RHHeats, Heat as RHHeat
from RHTypes.RHPilotTypes import Pilots as RHPilots
from RHTypes.RHClassTypes import Classes as RHClasses, Class as RHClass
from RHTypes.RHResultTypes import Results as RHResults

from TemplateTypes import (
        EliminationOpponent as TEliminationOpponent,
        EliminationResults as TEliminationResults,
        EliminationTrack as TEliminationTrack,
        EliminationStage as TEliminationStage,
        EliminationGroup as TEliminationGroup,
        EliminationRound as TEliminationRound,
        EliminationMatch as TEliminationMatch,
        EliminationParticipant as TEliminationParticipant,
        EliminationRoundMeta as TEliminationRoundMeta,
)

from converters.results_converters.results_converter_types import ResultConverter

import json
import logging
import copy

def heat_slot_to_opponent(h: RHHeat, r: Optional[RHResults], idx: int) -> TEliminationOpponent:
    if len(h.slots) <= idx:
        return TEliminationOpponent(id=0, score="-", result=None)
    pilot_id = h.slots[idx].pilot_id

    if (not r or
            str(h.id) not in r.heats or
            r.heats[str(h.id)].leaderboard is None):
        return TEliminationOpponent(id=pilot_id, score="-", result=None)

    score = None

    for rh_round in r.heats[str(h.id)].rounds:
        if rh_round.leaderboard is None:
            continue
        for lb_entry in rh_round.leaderboard.by_race_time:
            if lb_entry.pilot_id != pilot_id:
                continue

            if lb_entry.position is not None:
                if score is None:
                    score = 0
                score += lb_entry.position

    res = TEliminationOpponent(
            id = pilot_id,
            score = score if score is not None else "-",
            result = None)
    return res

class EliminationsResultsConverter(ResultConverter):

    @staticmethod
    def name() -> str:
        return "eliminations"

    @classmethod
    def convert(cls,
            r: Optional[RHResults],
            p: Optional[RHPilots],
            c: Optional[RHClasses],
            h: Optional[RHHeats],
            relevant_classes: list[int]) -> TEliminationResults:
        # a small helper to parse round meta
        def parse_meta(rh_class: RHClass):
            # Attempt to parse class information
            try:
                meta = TEliminationRoundMeta(**json.loads(rh_class.description))
                return meta
            except Exception as e:
                logging.warning(f"Invalid JSON for class {e} for \"{rh_class.description}\"")
                return None

        common_track = TEliminationTrack(
            stage=[TEliminationStage(
                id=0,
                name="1st Elimination Track",
                type="single_elimination",
                settings={}
            )],
            group=[TEliminationGroup(
                id=0,
                stage_id=0,
                number=1
            )],
            participant=[],
            round=[],
            match=[],
            match_game=[]
        )

        # fill in participants
        if p:
            for pilot in p.pilots:
                common_track.participant.append(TEliminationParticipant(
                    id=pilot.pilot_id,
                    name=pilot.callsign
                ))

        # fill in rounds (we will use class_id as round_id which will be unique across
        # all tracks, not just in individual one. What is more, these rounds will be dublicated
        # on all tracks, which is maybe not very efficient, but simpler
        if c:
            for rh_class in c.classes:
                # Filter out non-elimination classes
                if rh_class.id not in relevant_classes:
                    continue

                meta = parse_meta(rh_class)
                if not meta:
                    continue

                common_track.round.append(TEliminationRound(
                    id=rh_class.id,
                    number=meta.number,
                    stage_id=0,
                    group_id=0
                    ))

        # from now on we have filled all common infromation between different tracks.
        # therefore we will copy `elim_info` and fill in matches, which are unique
        # per track (winners track/loosers track)
        heats_by_class: dict[int, list[tuple[RHHeat, TEliminationRoundMeta]]] = {}
        elim_info = TEliminationResults(track={})
        if c and h:
            for rh_class in c.classes:
                # Filter out non-elimination classes
                if rh_class.id not in relevant_classes:
                    continue

                meta = parse_meta(rh_class)
                if not meta:
                    continue

                # Make sure that track exists
                if meta.track not in elim_info.track:
                    elim_info.track[meta.track] = copy.deepcopy(common_track)
                    elim_info.track[meta.track].stage[0].name = meta.displayname

                # Now go though each relevant heat and index it by class
                for heat in h.heats:
                    if heat.class_id != rh_class.id:
                        continue
                    if heat.class_id not in heats_by_class:
                        heats_by_class[heat.class_id] = [(heat, meta)]
                    else:
                        heats_by_class[heat.class_id].append((heat, meta))

            for class_id, heats in heats_by_class.items():
                heats_sorted = natsorted(heats, key=lambda x: x[0].displayname)
                for heat_number, heat_with_meta in enumerate(heats_sorted):
                    heat, meta = heat_with_meta

                    elim_info.track[meta.track].match.append(TEliminationMatch(
                        id=heat.id,
                        number=heat_number+1,
                        stage_id=0,
                        group_id=0,
                        round_id=class_id,
                        child_count=0,
                        status=0,
                        custom_label=heat.displayname,
                        opponent1=heat_slot_to_opponent(heat, r, 0),
                        opponent2=heat_slot_to_opponent(heat, r, 1),
                        opponent3=heat_slot_to_opponent(heat, r, 2),
                        opponent4=heat_slot_to_opponent(heat, r, 3),
                        previous_connection_type=meta.previous_connection_type,
                        next_connection_type=meta.next_connection_type,
                    ))

        return elim_info

