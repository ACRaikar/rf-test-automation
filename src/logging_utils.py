import csv
import pathlib
import math
import json
import re
import pyvisa
from pyvisa import VisaIOError
from datetime import datetime
from contextlib import contextmanager

def log_reading(filepath, timestamp, voltage, status):
    file_path = pathlib.Path(filepath)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['timestamp', 'voltage', 'status'])
            writer.writeheader()

    with open(filepath, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['timestamp', 'voltage', 'status'])
        writer.writerow({'timestamp': timestamp, 'voltage': voltage, 'status': status})

def read_log(filepath):
    with open(filepath, "r", newline='') as cfile:
        reader = csv.DictReader(cfile)
        return list(reader)

def summarize_run(filepath):
    readings = read_log(filepath)
    total_readings = len(readings)

    if total_readings == 0:
        return {"total_readings": 0, "pass_count": 0, "fail_count": 0, "error_count": 0,
                "min_voltage": None, "max_voltage": None, "average_voltage": None}

    pass_count = 0
    fail_count = 0
    error_count = 0

    for reading in readings:
        status = reading['status']
        if status == "PASS":
            pass_count += 1
        elif status == "FAIL":
            fail_count += 1
        else:
            error_count += 1

    valid = [r for r in readings if r['status'] in ('PASS', 'FAIL')]

    if not valid:
        return {"total_readings": total_readings, "pass_count": pass_count, "fail_count": fail_count,
                "error_count": error_count, "min_voltage": None, "max_voltage": None, "average_voltage": None}

    min_voltage = min(float(r['voltage']) for r in valid)
    max_voltage = max(float(r['voltage']) for r in valid)
    average_voltage = sum(float(r['voltage']) for r in valid) / len(valid)

    return {"total_readings": total_readings, "pass_count": pass_count, "fail_count": fail_count,
            "error_count": error_count, "min_voltage": min_voltage, "max_voltage": max_voltage,
            "average_voltage": average_voltage}


@contextmanager
def open_instrument(resource_string):
    rm = pyvisa.ResourceManager()
    inst = None
    try:
        inst = rm.open_resource(resource_string)
        yield inst
    finally:
        if inst is not None:
            inst.close()
        rm.close()

def check_voltage_core(inst, target, tolerance=0.01):
    """Pure logic — takes an already-open inst. This is what gets unit-tested."""
    try:
        reading = float(inst.query("VOLT?"))
    except VisaIOError:
        return None, "ERROR"
    except ValueError:
        return None, "ERROR"

    if math.isclose(reading, target, rel_tol=tolerance):
        return reading, "PASS"
    else:
        return reading, "FAIL"


def check_voltage(resource_string, target, tolerance=0.01):
    """Thin wrapper for a single one-off check against real hardware."""
    with open_instrument(resource_string) as inst:
        return check_voltage_core(inst, target, tolerance)

def sweep_voltages_core(inst, targets, filepath):
    """Testable — takes an already-open inst, no resource management."""
    for target in targets:
        timestamp = datetime.now().isoformat()
        reading, status = check_voltage_core(inst, target, tolerance=0.01)
        log_reading(filepath, timestamp, reading, status)

def sweep_voltages(resource_string, targets, filepath):
    """Opens the connection ONCE, reuses it across every target in the sweep."""
    with open_instrument(resource_string) as inst:
        for target in targets:
            timestamp = datetime.now().isoformat()
            reading, status = check_voltage_core(inst, target, tolerance=0.01)
            log_reading(filepath, timestamp, reading, status)

pattern = re.compile(
    r"(?P<date>\d{4}-\d{2}-\d{2})T(?P<time>\d{2}:\d{2}:\d{2})Z\s+"
    r"inst=(?P<inst>\w+)\s+" 
    r"setpoint=(?P<setpoint>[\d.]+)\s+"
    r"actual=(?P<actual>[\d.]+)\s+"
    r"delta=(?P<delta>-?[\d.]+)"
)

pattern2 = re.compile(
    r"(?P<timestamp>[\d-]+\s[\d:]+),"
    r"(?P<voltage>[-\d.]+),"
    r"(?P<status>\w+)"
)

pattern3 = re.compile(
    r"error_code=(?P<error_code>-?\d+)"
)

PATTERNS = [pattern, pattern2]  # module-level, compiled once

def parse_log_line(line):
    for p in PATTERNS:
        match = p.search(line)
        if match:
            return match.groupdict()
    return None

def parse_log_file(filepath):
    results = []
    with open(filepath) as f:
        for line in f:
            parsed = parse_log_line(line)
            if parsed is not None:
                results.append(parsed)
    return results

def extract_error_codes(line):
    return pattern3.findall(line)


if __name__ == "__main__":
    log_reading('Measurements.csv', '2024-06-01 12:00:00', 3.3, 'PASS')
    log_reading('Measurements.csv', '2024-06-01 12:05:00', 3.5, 'FAIL')
    log_reading('Measurements.csv', '2024-06-01 12:10:00', '', 'ERROR')
    print(json.dumps(summarize_run('Measurements.csv'), indent=4))