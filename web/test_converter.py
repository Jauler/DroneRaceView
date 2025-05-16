import pytest
import json
from RHTypes.RHClassTypes import Classes
from RHTypes.RHHeatTypes import Heats
from RHTypes.RHRaceStatusTypes import RaceStatus
from RHTypes.RHPilotTypes import Pilots
from RHTypes.RHResultTypes import Results
from RHTypes.RHFrequencyTypes import Frequencies
from TemplateTypes import PilotResult, HeatPilot
from pathlib import Path
import converter

SCRIPT_DIR = Path(__file__).resolve().parent

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
    results = Results(**json.load(open(SCRIPT_DIR / results_filename)))
    heats = Heats(**json.load(open(SCRIPT_DIR / heats_filename)))
    pilots = Pilots(**json.load(open(SCRIPT_DIR / pilots_filename)))
    classes = Classes(**json.load(open(SCRIPT_DIR / classes_filename)))
    frequency = Frequencies(**json.load(open(SCRIPT_DIR / freq_filename)))

    pr = converter.rounds(results, heats, classes, pilots, frequency)

    assert len(pr) == 4
    assert len(pr[0].heats) == 0
    assert len(pr[1].heats) == 0
    assert len(pr[2].heats) == 0
    assert len(pr[3].heats) == 2
    assert len(pr[3].heats[0].pilots) == 4
    assert pr[3].heats[0].pilots == [
        HeatPilot(
            pilot_id=26,
            channel='R2 (5695 Mhz)',
            nickname='Jauler',
            position='1',
            gains='N/A',
            points='N/A'
        ),
        HeatPilot(
            pilot_id=2,
            channel='R3 (5732 Mhz)',
            nickname='Edga',
            position='2',
            gains='N/A',
            points='N/A'
        ),
        HeatPilot(
            pilot_id=15,
            channel='R6 (5843 Mhz)',
            nickname='Armis',
            position='3',
            gains='N/A',
            points='N/A'
        ),
        HeatPilot(
            pilot_id=68,
            channel='R7 (5880 Mhz)',
            nickname='Goo',
            position='4',
            gains='N/A',
            points='N/A'
        )
    ]
    assert pr[3].heats[1].pilots == [
        HeatPilot(channel='R2 (5695 Mhz)',
            pilot_id=21,
            nickname='Goreez',
            position='N/A',
            gains='N/A',
            points='N/A'
        ),
        HeatPilot(channel='R3 (5732 Mhz)',
            pilot_id=13,
            nickname='AM14',
            position='N/A',
            gains='N/A',
            points='N/A'
        ),
        HeatPilot(channel='R6 (5843 Mhz)',
            pilot_id=5,
            nickname='ChirpFPV',
            position='N/A',
            gains='N/A',
            points='N/A'
        ),
        HeatPilot(channel='R7 (5880 Mhz)',
            pilot_id=60,
            nickname='Dainius',
            position='N/A',
            gains='N/A',
            points='N/A'
        )
    ]


