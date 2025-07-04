import pytest
import json
from RHTypes.RHClassTypes import Classes
from RHTypes.RHHeatTypes import Heats
from RHTypes.RHRaceStatusTypes import RaceStatus
from RHTypes.RHPilotTypes import Pilots
from RHTypes.RHResultTypes import Results
from RHTypes.RHFrequencyTypes import Frequencies
from RHTypes.RHFormatTypes import Formats
from TemplateTypes import PilotResult, HeatPilot
from pathlib import Path

@pytest.mark.parametrize("filename", [
    "testdata/class_data_sample_1.json",
    "testdata/class_data_sample_2.json",
])
def test_rh_class_data(filename):
    _r = Classes(**json.load(open(filename)))

@pytest.mark.parametrize("filename", [
    "testdata/frequency_data_sample_1.json"
])
def test_rh_frequency_data(filename):
    _r = Frequencies(**json.load(open(filename)))

@pytest.mark.parametrize("filename", [
    "testdata/heat_data_sample_1.json",
    "testdata/heat_data_sample_2.json",
    "testdata/heat_data_sample_3.json"
])
def test_rh_heat_data(filename):
    _r = Heats(**json.load(open(filename)))

@pytest.mark.parametrize("filename", [
    "testdata/pilot_data_sample_1.json",
    "testdata/pilot_data_sample_2.json"
])
def test_rh_pilot_data(filename):
    _r = Pilots(**json.load(open(filename)))

@pytest.mark.parametrize("filename", [
    "testdata/race_status_data_sample_1.json",
    "testdata/race_status_data_sample_2.json",
])
def test_rh_race_status(filename):
    _r = RaceStatus(**json.load(open(filename)))

@pytest.mark.parametrize("filename", [
    "testdata/result_data_sample_1.json",
    "testdata/result_data_sample_2.json",
    "testdata/result_data_sample_3.json",
    "testdata/result_data_sample_4.json",
])
def test_rh_result_data(filename):
    _r = Results(**json.load(open(filename)))

@pytest.mark.parametrize("filename", [
    "testdata/format_data_sample_1.json",
])
def test_rh_format_data(filename):
    _r = Formats(**json.load(open(filename)))



