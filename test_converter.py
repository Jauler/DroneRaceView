import pytest
import json
from RHTypes.RHClassTypes import Classes
from RHTypes.RHHeatTypes import Heats
from RHTypes.RHRaceStatusTypes import RaceStatus
from RHTypes.RHPilotTypes import Pilots
from RHTypes.RHResultTypes import Results
from RHTypes.RHFrequencyTypes import Frequencies
from TemplateTypes import PilotResult, HeatPilot
import converter

@pytest.mark.parametrize("race_status_filename", [
    "testdata/race_status_data_sample_1.json",
])
@pytest.mark.parametrize("heats_filename", [
    "testdata/heat_data_sample_1.json",
    "testdata/heat_data_sample_2.json"
])
def test_current_heat_converter(race_status_filename, heats_filename):
    race_status = RaceStatus(**json.load(open(race_status_filename)))
    heats = Heats(**json.load(open(heats_filename)))

    current_heat = converter.current_heat(race_status, heats)

    assert current_heat == "SundayWhoop Qualifier 3"

@pytest.mark.parametrize("race_status_filename", [
    "testdata/race_status_data_sample_1.json",
])
@pytest.mark.parametrize("heats_filename", [
    "testdata/heat_data_sample_1.json",
])
def test_current_heat_converter_null_heat(race_status_filename, heats_filename):
    race_status = RaceStatus(**json.load(open(race_status_filename)))
    heats = Heats(**json.load(open(heats_filename)))

    race_status.race_heat_id = 0

    current_heat = converter.current_heat(race_status, heats)

    assert current_heat == "N/A"


@pytest.mark.parametrize("race_status_filename", [
    "testdata/race_status_data_sample_1.json",
])
@pytest.mark.parametrize("heats_filename", [
    "testdata/heat_data_sample_1.json",
])
@pytest.mark.parametrize("pilots_filename", [
    "testdata/pilot_data_sample_1.json"
])
@pytest.mark.parametrize("freq_filename", [
    "testdata/frequency_data_sample_1.json"
])
def test_current_pilots_converter(race_status_filename, heats_filename, pilots_filename, freq_filename):
    race_status = RaceStatus(**json.load(open(race_status_filename)))
    heats = Heats(**json.load(open(heats_filename)))
    pilots = Pilots(**json.load(open(pilots_filename)))
    frequency = Frequencies(**json.load(open(freq_filename)))

    current_pilots = converter.current_pilots(race_status, heats, pilots, frequency)

    assert len(current_pilots) == 4
    assert current_pilots[0].nickname == "Armis"
    assert current_pilots[0].channel == "R2 (5695 Mhz)"
    assert current_pilots[1].nickname == "BatOnTopas"
    assert current_pilots[1].channel == "R3 (5732 Mhz)"
    assert current_pilots[2].nickname == ""
    assert current_pilots[2].channel == "R6 (5843 Mhz)"
    assert current_pilots[3].nickname == ""
    assert current_pilots[3].channel == "R7 (5880 Mhz)"


@pytest.mark.parametrize("results_filename", [
    "testdata/result_data_sample_1.json"
])
@pytest.mark.parametrize("heats_filename", [
    "testdata/heat_data_sample_3.json"
])
@pytest.mark.parametrize("pilots_filename", [
    "testdata/pilot_data_sample_2.json"
])
def test_current_pilots_converter_pilot_results(results_filename, heats_filename, pilots_filename):
    results = Results(**json.load(open(results_filename)))
    heats = Heats(**json.load(open(heats_filename)))
    pilots = Pilots(**json.load(open(pilots_filename)))

    pr = converter.pilot_results(results, heats, pilots)

    assert len(pr) == len(pilots.pilots)
    assert pr[0] == PilotResult(
            rank=1,
            nickname='Jauler',
            points=1050,
            fastest_lap='0:04.390',
            fastest_lap_source='QF1',
            fastest_3_laps='0:38.225',
            fastest_3_laps_source='QF1',
            next_heat="N/A")
    assert pr[1] == PilotResult(
            rank=2,
            nickname='Edga',
            points=1020,
            fastest_lap='0:06.377',
            fastest_lap_source='QF1',
            fastest_3_laps='0:39.122',
            fastest_3_laps_source='QF1',
            next_heat="N/A")
    assert pr[2] == PilotResult(
            rank=3,
            nickname='3RC',
            points=1000,
            fastest_lap='N/A',
            fastest_lap_source='N/A',
            fastest_3_laps='N/A',
            fastest_3_laps_source='N/A',
            next_heat="N/A")
    assert pr[5] == PilotResult(
            rank=3,
            nickname='AM14',
            points=1000,
            fastest_lap='N/A',
            fastest_lap_source='N/A',
            fastest_3_laps='N/A',
            fastest_3_laps_source='N/A',
            next_heat='QF2')
    assert pr[-2] == PilotResult(rank=4,
            nickname='Armis',
            points=980,
            fastest_lap='0:08.048',
            fastest_lap_source='QF1',
            fastest_3_laps='0:40.721',
            fastest_3_laps_source='QF1',
            next_heat="N/A")
    assert pr[-1] == PilotResult(
            rank=5,
            nickname='Goo',
            points=950,
            fastest_lap='0:09.663',
            fastest_lap_source='QF1',
            fastest_3_laps='0:41.096',
            fastest_3_laps_source='QF1',
            next_heat="N/A")


@pytest.mark.parametrize("results_filename", [
    "testdata/result_data_sample_1.json"
])
@pytest.mark.parametrize("heats_filename", [
    "testdata/heat_data_sample_3.json"
])
@pytest.mark.parametrize("pilots_filename", [
    "testdata/pilot_data_sample_2.json"
])
@pytest.mark.parametrize("classes_filename", [
    "testdata/class_data_sample_2.json"
])
@pytest.mark.parametrize("freq_filename", [
    "testdata/frequency_data_sample_1.json"
])
def test_rounds_converter(results_filename, heats_filename, pilots_filename, classes_filename, freq_filename):
    results = Results(**json.load(open(results_filename)))
    heats = Heats(**json.load(open(heats_filename)))
    pilots = Pilots(**json.load(open(pilots_filename)))
    classes = Classes(**json.load(open(classes_filename)))
    frequency = Frequencies(**json.load(open(freq_filename)))

    pr = converter.rounds(results, heats, classes, pilots, frequency)

    assert len(pr) == 4
    assert len(pr[0].heats) == 2
    assert len(pr[1].heats) == 0
    assert len(pr[2].heats) == 0
    assert len(pr[3].heats) == 0
    assert len(pr[0].heats[0].pilots) == 4
    assert pr[0].heats[0].pilots == [
        HeatPilot(
            channel='R2 (5695 Mhz)',
            nickname='Jauler',
            position='1',
            gains='50',
            points='1050'
        ),
        HeatPilot(
            channel='R3 (5732 Mhz)',
            nickname='Edga',
            position='2',
            gains='20',
            points='1020'
        ),
        HeatPilot(
            channel='R6 (5843 Mhz)',
            nickname='Armis',
            position='3',
            gains='-20',
            points='980'
        ),
        HeatPilot(
            channel='R7 (5880 Mhz)',
            nickname='Goo',
            position='4',
            gains='-50',
            points='950'
        )
    ]
    assert pr[0].heats[1].pilots == [
        HeatPilot(channel='R2 (5695 Mhz)',
            nickname='Goreez',
            position='N/A',
            gains='N/A',
            points='N/A'
        ),
        HeatPilot(channel='R3 (5732 Mhz)',
            nickname='AM14',
            position='N/A',
            gains='N/A',
            points='N/A'
        ),
        HeatPilot(channel='R6 (5843 Mhz)',
            nickname='ChirpFPV',
            position='N/A',
            gains='N/A',
            points='N/A'
        ),
        HeatPilot(channel='R7 (5880 Mhz)',
            nickname='Dainius',
            position='N/A',
            gains='N/A',
            points='N/A'
        )
    ]


