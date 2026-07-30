import csv
import pathlib
import math
import json

def log_reading(filepath,timestamp, voltage):
    file_path = pathlib.Path(filepath)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    if not file_path.exists():
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['timestamp', 'voltage'])
            writer.writeheader()

    with open(filepath, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['timestamp', 'voltage'])
        writer.writerow({'timestamp': timestamp, 'voltage': voltage})

def read_log(filepath):
    with open(filepath, "r", newline='') as cfile:
        reader = csv.DictReader(cfile)
        return list(reader)

def summarize_run(filepath, target, tolerance):
    readings = read_log(filepath)
    total_readings = len(readings)

    if total_readings == 0:
        return {"total_readings": 0, "pass_count": 0, "fail_count": 0, "min_voltage": None, "max_voltage": None, "average_voltage": None}

    pass_count = 0
    fail_count = 0

    for reading in readings:
        voltage = float(reading['voltage'])
        status = math.isclose(voltage, target, rel_tol=tolerance)
        if status:
            pass_count += 1
        else:
            fail_count += 1
    min_voltage = min(float(r['voltage']) for r in readings)
    max_voltage = max(float(r['voltage']) for r in readings)
    average_voltage = sum(float(r['voltage']) for r in readings) / total_readings
    return {"total_readings": total_readings, "pass_count": pass_count, "fail_count": fail_count, "min_voltage": min_voltage, "max_voltage": max_voltage, "average_voltage": average_voltage}

if __name__ == "__main__":
    log_reading('logs/Measurements.csv', '2024-06-01 12:00:00', 3.3)
    log_reading('Measurements.csv', '2024-06-01 12:00:00', 3.3)
    log_reading('Measurements.csv', '2024-06-01 12:05:00', 3.5)
    log_reading('Measurements.csv', '2024-06-01 12:10:00', 2.8)
    read_log('Measurements.csv')
    print(json.dumps(summarize_run('Measurements.csv', target=3.3, tolerance=0.1), indent=4))

