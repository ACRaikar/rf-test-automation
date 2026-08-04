import csv
import pathlib
import math
import json
import pyvisa
from pyvisa import VisaIOError
from datetime import datetime

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

def check_voltage(resource_string, target, tolerance=0.01):
    rm = pyvisa.ResourceManager()
    inst = None
    try:
        inst = rm.open_resource(resource_string)
        reading = float(inst.query("VOLT?"))
    except VisaIOError as e:
        reading = None
        return reading, "ERROR"
    finally:
        if inst:
            inst.close()
    
    if math.isclose(reading, target, rel_tol=tolerance):
        return reading, "PASS" 
    else:
        return reading, "FAIL"

def sweep_voltages(resource_string, targets,filepath):
    for target in targets:
        timestamp = datetime.now().isoformat()
        try:
            reading, status = check_voltage(resource_string, target, tolerance=0.01)
            log_reading(filepath, timestamp, reading, status)
        except VisaIOError as e:
            reading = f"Error - {e}"
            status = "ERROR"
            log_reading(filepath, timestamp, reading,status)
            continue
        
if __name__ == "__main__":
    log_reading('Measurements.csv', '2024-06-01 12:00:00', 3.3, 'PASS')
    log_reading('Measurements.csv', '2024-06-01 12:05:00', 3.5, 'FAIL')
    log_reading('Measurements.csv', '2024-06-01 12:10:00', '', 'ERROR')
    print(json.dumps(summarize_run('Measurements.csv'), indent=4))