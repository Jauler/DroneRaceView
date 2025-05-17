import pytest
import json
from pathlib import Path
from RHTypes.RHResultTypes import Leaderboard, LeaderboardResultSource, Results, LeaderboardEntry

from results_converter import ConsecutivesResultConverter

import copy

SCRIPT_DIR = Path(__file__).resolve().parent
EMPTY_LB_ENTRY = LeaderboardEntry(
        pilot_id=1,
        callsign="testpilot",
        team_name=None,
        laps=0,
        starts=0,
        node=0,
        total_time="0:00.000",
        total_time_laps="0:00.000",
        last_lap=None,
        average_lap="0:00.000",
        fastest_lap="0:00.000",
        consecutives="",
        consecutives_base=0,
        consecutive_lap_start=None,
        fastest_lap_source = None,
        consecutives_source = None,
        total_time_raw = 0.0,
        total_time_laps_raw = 0.0,
        average_lap_raw = 0.0,
        fastest_lap_raw = 0.0,
        consecutives_raw = None,
        last_lap_raw = None,
        position = None)


def zeroize_unmerged_lb_entry_fields(entry):
    entry.position = None
    entry.last_lap = ''
    entry.last_lap_raw = 0.0
    entry.node = 0

@pytest.mark.parametrize("results_filename", [
    "testdata/result_data_sample_1.json",
    "testdata/result_data_sample_2.json",
    "testdata/result_data_sample_3.json",
    "testdata/result_data_sample_4.json",
    "testdata/result_data_sample_6_picnic_race.json",
])
def test_milliseconds_format(results_filename):
    assert ConsecutivesResultConverter
    results = Results(**json.load(open(SCRIPT_DIR / results_filename)))

    for heat in results.heats.values():
        assert heat.leaderboard
        for lb_entry in heat.leaderboard.by_consecutives:
            avg_formatted = ConsecutivesResultConverter.format_milliseconds(lb_entry.average_lap_raw)
            assert avg_formatted == lb_entry.average_lap

            fastest_formatted = ConsecutivesResultConverter.format_milliseconds(lb_entry.fastest_lap_raw)
            assert fastest_formatted == lb_entry.fastest_lap

@pytest.mark.parametrize("results_filename", [
    "testdata/result_data_sample_1.json",
    "testdata/result_data_sample_2.json",
    "testdata/result_data_sample_3.json",
    "testdata/result_data_sample_4.json",
    "testdata/result_data_sample_5.json",
    "testdata/result_data_sample_6_picnic_race.json",
])
def test_lb_entry_comparison(results_filename):
    # This test ensures that rotorhazard "sorting" of consecutives leaderboard
    # is consistent with ConsecutivesResultConverter implementation
    results = Results(**json.load(open(SCRIPT_DIR / results_filename)))

    for heat in results.heats.values():
        assert heat.leaderboard
        for i in range(1, len(heat.leaderboard.by_consecutives)):
            faster_lb_entry = heat.leaderboard.by_consecutives[i-1]
            slower_lb_entry = heat.leaderboard.by_consecutives[i]

            assert ConsecutivesResultConverter.cmp_lb_entries(faster_lb_entry, slower_lb_entry) <= 0
            assert ConsecutivesResultConverter.cmp_lb_entries(slower_lb_entry, slower_lb_entry) == 0
            assert ConsecutivesResultConverter.cmp_lb_entries(faster_lb_entry, faster_lb_entry) == 0
            assert ConsecutivesResultConverter.cmp_lb_entries(slower_lb_entry, faster_lb_entry) >= 0

    for rh_class in results.classes.values():
        if not rh_class.leaderboard:
            continue
        assert rh_class.leaderboard
        for i in range(1, len(rh_class.leaderboard.by_consecutives)):
            faster_lb_entry = rh_class.leaderboard.by_consecutives[i-1]
            slower_lb_entry = rh_class.leaderboard.by_consecutives[i]

            assert ConsecutivesResultConverter.cmp_lb_entries(faster_lb_entry, slower_lb_entry) <= 0
            assert ConsecutivesResultConverter.cmp_lb_entries(slower_lb_entry, slower_lb_entry) == 0
            assert ConsecutivesResultConverter.cmp_lb_entries(faster_lb_entry, faster_lb_entry) == 0
            assert ConsecutivesResultConverter.cmp_lb_entries(slower_lb_entry, faster_lb_entry) >= 0

@pytest.mark.parametrize("results_filename", [
    "testdata/result_data_sample_1.json",
    "testdata/result_data_sample_2.json",
    "testdata/result_data_sample_3.json",
    "testdata/result_data_sample_4.json",
    "testdata/result_data_sample_5.json",
    "testdata/result_data_sample_6_picnic_race.json",
])
def test_lb_entry_merge(results_filename):
    # This test ensures that rotorhazard merging of leaderboards (e.g. merging all
    # singular heat leaderboard should be consistent with class leaderboard
    results = Results(**json.load(open(SCRIPT_DIR / results_filename)))

    for rh_class_id, heat_ids in results.heats_by_class.items():
        merged_lbs = {}
        if rh_class_id not in results.classes: # There may be classless heats
            continue
        if not results.classes[rh_class_id].leaderboard:
            continue

        for heat_id in heat_ids:
            if str(heat_id) not in results.heats:
                continue
            heat = results.heats[str(heat_id)]
            if not heat.leaderboard:
                continue

            # Attempt to merge A <- B
            for lb_entry in heat.leaderboard.by_consecutives:
                if lb_entry.pilot_id not in merged_lbs:
                    merged_lbs[lb_entry.pilot_id] = lb_entry
                else:
                    old_entry = merged_lbs[lb_entry.pilot_id]
                    new_entry = lb_entry
                    merged_lbs[lb_entry.pilot_id] = ConsecutivesResultConverter.merge_leaderboard_entries(old_entry, new_entry)

                    # verify, that merge in the other direction provides the same result
                    assert merged_lbs[lb_entry.pilot_id] == ConsecutivesResultConverter.merge_leaderboard_entries(new_entry, old_entry)


        class_lb = results.classes[rh_class_id].leaderboard
        assert class_lb
        for lb_entry in class_lb.by_consecutives:
            assert lb_entry.pilot_id in merged_lbs
            merged_lb_entry = merged_lbs[lb_entry.pilot_id]

            # zeroize potentially non-merged fields
            zeroize_unmerged_lb_entry_fields(lb_entry)
            zeroize_unmerged_lb_entry_fields(merged_lb_entry)

            assert lb_entry == merged_lb_entry


def test_lb_entry_merge_empty():
    lb_entry = EMPTY_LB_ENTRY
    merged_lb_entry = ConsecutivesResultConverter.merge_leaderboard_entries(EMPTY_LB_ENTRY, EMPTY_LB_ENTRY)

    # Zeroize unmerged LB entry fields
    zeroize_unmerged_lb_entry_fields(lb_entry)
    zeroize_unmerged_lb_entry_fields(merged_lb_entry)

    assert merged_lb_entry == EMPTY_LB_ENTRY


def test_lb_entry_merge_with_different_consecutives_base():
    lb_entry_1 = copy.deepcopy(EMPTY_LB_ENTRY)
    lb_entry_2 = copy.deepcopy(EMPTY_LB_ENTRY)
    expected_lb_entry = copy.deepcopy(EMPTY_LB_ENTRY)

    lb_entry_1.consecutives_base = 2
    lb_entry_1.consecutives_raw = 60.1
    lb_entry_1.consecutive_lap_start = 1
    lb_entry_1.consecutives_source = LeaderboardResultSource(round = 2, heat = 2, displayname="test1")
    lb_entry_1.consecutives = '0:00.060'

    lb_entry_2.consecutives_base = 3
    lb_entry_2.consecutives_raw = 160.1
    lb_entry_2.consecutive_lap_start = 1
    lb_entry_2.consecutives_source = LeaderboardResultSource(round = 3, heat = 3, displayname="test2")
    lb_entry_2.consecutives = '0:00.160'

    expected_lb_entry.consecutives_base = lb_entry_2.consecutives_base
    expected_lb_entry.consecutives_raw = lb_entry_2.consecutives_raw
    expected_lb_entry.consecutive_lap_start = lb_entry_2.consecutive_lap_start
    expected_lb_entry.consecutives_source = lb_entry_2.consecutives_source
    expected_lb_entry.consecutives = lb_entry_2.consecutives

    assert expected_lb_entry == ConsecutivesResultConverter.merge_leaderboard_entries(lb_entry_2, lb_entry_1)
    assert expected_lb_entry == ConsecutivesResultConverter.merge_leaderboard_entries(lb_entry_1, lb_entry_2)


@pytest.mark.parametrize("results_filename", [
    "testdata/result_data_sample_1.json",
    "testdata/result_data_sample_2.json",
    "testdata/result_data_sample_3.json",
    "testdata/result_data_sample_4.json",
    "testdata/result_data_sample_5.json",
    "testdata/result_data_sample_6_picnic_race.json",
])
def test_lb_merging_heats_to_class(results_filename):
    # This test ensures that rotorhazard merging of leaderboards (e.g. merging all
    # singular heat leaderboard should be consistent with class leaderboard
    results = Results(**json.load(open(SCRIPT_DIR / results_filename)))

    for rh_class_id, heat_ids in results.heats_by_class.items():
        merged_lb = None
        if rh_class_id not in results.classes: # There may be classless heats
            continue
        if not results.classes[rh_class_id].leaderboard:
            continue

        for heat_id in heat_ids:
            if str(heat_id) not in results.heats:
                continue
            heat = results.heats[str(heat_id)]
            assert heat.leaderboard
            lb = heat.leaderboard.by_consecutives

            if merged_lb is None:
                merged_lb = lb
            else:
                merged_lb = ConsecutivesResultConverter.merge_leaderboards(merged_lb, lb)

        assert merged_lb

        # Zeroize lb entries
        rh_class = results.classes[rh_class_id]
        assert rh_class.leaderboard
        class_lb = rh_class.leaderboard.by_consecutives
        for entry in class_lb:
            zeroize_unmerged_lb_entry_fields(entry)
        for entry in merged_lb:
            zeroize_unmerged_lb_entry_fields(entry)

        assert class_lb == merged_lb

@pytest.mark.parametrize("results_filename", [
    "testdata/result_data_sample_1.json",
    "testdata/result_data_sample_2.json",
    "testdata/result_data_sample_3.json",
    "testdata/result_data_sample_4.json",
    "testdata/result_data_sample_5.json",
    "testdata/result_data_sample_6_picnic_race.json",

])
def test_lb_merging_heats_to_event(results_filename):
    # This test ensures that rotorhazard merging of leaderboards (e.g. merging all
    # singular heat leaderboard should be consistent with class leaderboard
    results = Results(**json.load(open(SCRIPT_DIR / results_filename)))

    merged_lb = None
    for heat in results.heats.values():
        if not heat.leaderboard:
            continue

        lb = heat.leaderboard.by_consecutives

        if merged_lb is None:
            merged_lb = lb
        else:
            merged_lb = ConsecutivesResultConverter.merge_leaderboards(merged_lb, lb)

    assert merged_lb

    # Zeroize lb entries
    assert results.event_leaderboard
    event_lb = results.event_leaderboard.by_consecutives

    for entry in event_lb:
        zeroize_unmerged_lb_entry_fields(entry)
    for entry in merged_lb:
        zeroize_unmerged_lb_entry_fields(entry)

    assert event_lb == merged_lb


