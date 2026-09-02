from logging_utils import parse_log_line

def test_parse_log_line_warn_format():
    line = "[WARN] 2026-08-10T14:32:07Z inst=PSU1 setpoint=5.0 actual=4.87 delta=0.13"
    result = parse_log_line(line)
    assert result == {
        'date': '2026-08-10', 'time': '14:32:07', 'inst': 'PSU1',
        'setpoint': '5.0', 'actual': '4.87', 'delta': '0.13'
    }

def test_parse_log_line_csv_format():
    line = "2026-08-10 14:32:07,-4.998,FAIL"
    result = parse_log_line(line)
    assert result == {
        'timestamp': '2026-08-10 14:32:07',
        'voltage': '-4.998',
        'status': 'FAIL'
    }

def test_parse_log_line_nomatch_format():
    line = "System boot complete, no errors detected"
    result = parse_log_line(line)
    assert result is None