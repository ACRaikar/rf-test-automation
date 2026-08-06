import pyvisa
from pyvisa import VisaIOError
import pytest
from logging_utils import check_voltage_core

#Bad_Instrument
class BrokenInstrument:
    def query(self, command):
        raise VisaIOError(-1073807339)

@pytest.fixture
def bad_instrument():
    return BrokenInstrument()

def test_check_voltage_visa_error(bad_instrument):
    result3 = check_voltage_core(bad_instrument, target=5.0, tolerance = 0.01)
    assert "ERROR" in result3[1]

#Good_Instrument
class FakeInstrument:
    def __init__(self, reply):
        self.reply =reply

    def query(self,command):
        return self.reply

@pytest.fixture
def good_instrument():
    return FakeInstrument("5.01")

def test_check_voltage_passes_within_tolerance(good_instrument):
    result = check_voltage_core(good_instrument, target=5.0, tolerance = 0.01)
    assert "PASS" in result[1]

def test_check_voltage_fails_out_of_tolerance(good_instrument):
    result2 = check_voltage_core(good_instrument, target = 2.0, tolerance = 0.01)
    assert "FAIL" in result2[1]


#Logging execise
from logging_utils import log_reading, read_log

def test_fake_logging(tmp_path):
    path = tmp_path/"readings.csv"
    log_reading(path, timestamp="2024-06-01 12:10:00", voltage=4.99, status="PASS")
    data = read_log(path)
    assert "2024-06-01 12:10:00" == data[0]["timestamp"]
    assert "4.99" == data[0]["voltage"]
    assert "PASS" == data[0]["status"]


#Sweep-level_test
from logging_utils import sweep_voltages_core

class FakeSweepVoltage:
    def __init__(self, replies):
        self.replies = replies
        self.count=0

    def query(self, command):
        reply = self.replies[self.count]
        self.count+=1
        return reply

@pytest.fixture
def fake_sweep():
    return FakeSweepVoltage([5.0, 3.0, 4.99, 0, 5.01])

def test_sweep_level(tmp_path, fake_sweep):
    path = tmp_path/"voltage_test.csv"
    targets = [5.0, 5.0,5.0,5.0,5.0]
    sweep_voltages_core(fake_sweep, targets, path)
    data = read_log(path)
    assert "PASS" == data[0]["status"]
    assert "FAIL" == data[1]["status"]
    assert "PASS" == data[2]["status"]
    assert "FAIL" == data[3]["status"]
    assert "PASS" == data[4]["status"]
    assert len(data) == 5
