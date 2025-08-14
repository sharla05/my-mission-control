uv venv --python 3.13

uv lock

uv add fastapi uvicorn structlog python-multipart tomli

uv add pytest pytest-cov httpx pre-commit ruff isort pyright bandit --dev

input format
<timestamp>|<satellite-id>|<red-high-limit>|<yellow-high-limit>|<yellow-low-limit>|<red-low-limit>|<raw-value>|<component>


violation lines:  2018-01-01 23:01:09.521000 1000 17 15 9 8 7.8 BATT        <-
violation lines:  2018-01-01 23:01:38.001000 1000 101 98 25 20 102.9 TSTAT  <-
violation lines:  2018-01-01 23:02:11.302000 1000 17 15 9 8 7.7 BATT
violation lines:  2018-01-01 23:03:03.008000 1000 101 98 25 20 102.7 TSTAT
violation lines:  2018-01-01 23:03:05.009000 1000 101 98 25 20 101.2 TSTAT
violation lines:  2018-01-01 23:04:11.531000 1000 17 15 9 8 7.9 BATT
violation lines:  2018-01-01 23:05:07.421000 1001 17 15 9 8 7.9 BATT

violation lines:  2018-01-01 23:01:09.521000 1000 17 15 9 8 7.8 BATT        <-
violation lines:  2018-01-01 23:02:11.302000 1000 17 15 9 8 7.7 BATT
violation lines:  2018-01-01 23:04:11.531000 1000 17 15 9 8 7.9 BATT

violation lines:  2018-01-01 23:05:07.421000 1001 17 15 9 8 7.9 BATT


violation lines:  2018-01-01 23:01:38.001000 1000 101 98 25 20 102.9 TSTAT  <-
violation lines:  2018-01-01 23:03:03.008000 1000 101 98 25 20 102.7 TSTAT
violation lines:  2018-01-01 23:03:05.009000 1000 101 98 25 20 101.2 TSTAT

=================== battery only ======================
violation lines:  2018-01-01 23:01:09.521000 1000 17 15 9 8 7.8 BATT
violation lines:  2018-01-01 23:02:11.302000 1000 17 15 9 8 7.7 BATT
violation lines:  2018-01-01 23:04:11.531000 1000 17 15 9 8 7.9 BATT
violation lines:  2018-01-01 23:05:07.421000 1001 17 15 9 8 7.9 BATT

20180101 23:01:09.521|1000|17|15|9|8|7.8|BATT
20180101 23:02:11.302|1000|17|15|9|8|7.7|BATT
20180101 23:04:11.531|1000|17|15|9|8|7.9|BATT
20180101 23:05:07.421|1001|17|15|9|8|7.9|BATT

========================================== Tests =============================================
uv run pytest .\tests\integration\test_cli.py
uv run pytest .\tests\integration\test_process_log_file.py
uv run pytest tests/unit/test_logging_setup.py
uv run pytest .\tests\integration\test_log_parser.py

=================================================================================
from datetime import datetime
from unittest.mock import patch

from my_mission_control.alerter.alert_tracker import AlertTracker
from my_mission_control.alerter.log_line_parser import parse_log_lines_to_json
from my_mission_control.alerter.alert_generator import Alert

from alert.parser.parser import format_ts, make_log_line  # Or redefine locally if needed

@patch("my_mission_control.alerter.alert_tracker.evaluate_alert_condition")
def test_alert_tracker_with_sample_data(mock_eval):
    # Mock severity based on component
    def mock_severity(log_entry):
        return "RED HIGH" if log_entry.cmpnt == "TSTAT" else "RED LOW"
    mock_eval.side_effect = mock_severity

    tracker = AlertTracker()
    base_time = datetime(2018, 1, 1, 23, 1, 5)

    lines = [
        make_log_line(base_time, 1001, 101, 98, 25, 20, 99.9, "TSTAT"),
        make_log_line(base_time + timedelta(seconds=4.52), 1000, 17, 15, 9, 8, 7.8, "BATT"),
        make_log_line(base_time + timedelta(seconds=21.01), 1001, 101, 98, 25, 20, 99.8, "TSTAT"),
        make_log_line(base_time + timedelta(seconds=33.0), 1000, 101, 98, 25, 20, 102.9, "TSTAT"),
        make_log_line(base_time + timedelta(seconds=44.02), 1000, 101, 98, 25, 20, 87.9, "TSTAT"),
        make_log_line(base_time + timedelta(seconds=64.01), 1001, 101, 98, 25, 20, 89.3, "TSTAT"),
        make_log_line(base_time + timedelta(seconds=65.02), 1001, 101, 98, 25, 20, 89.4, "TSTAT"),
        make_log_line(base_time + timedelta(seconds=66.3), 1000, 17, 15, 9, 8, 7.7, "BATT"),
        make_log_line(base_time + timedelta(seconds=118.0), 1000, 101, 98, 25, 20, 102.7, "TSTAT"),
        make_log_line(base_time + timedelta(seconds=120.0), 1000, 101, 98, 25, 20, 101.2, "TSTAT"),
        make_log_line(base_time + timedelta(seconds=181.01), 1001, 101, 98, 25, 20, 89.9, "TSTAT"),
        make_log_line(base_time + timedelta(seconds=186.53), 1000, 17, 15, 9, 8, 7.9, "BATT"),
        make_log_line(base_time + timedelta(seconds=240.02), 1001, 101, 98, 25, 20, 89.9, "TSTAT"),
        make_log_line(base_time + timedelta(seconds=242.42), 1001, 17, 15, 9, 8, 7.9, "BATT"),
    ]

    log_entries = parse_log_lines_to_json(lines)

    alerts = []
    for entry in log_entries:
        alert = tracker.process_log_entry(entry)
        if alert:
            alerts.append(alert)

    # Print alerts for inspection
    for alert in alerts:
        print(f"ALERT: sat_id={alert.sat_id}, cmpnt={alert.cmpnt}, severity={alert.severity}, ts={alert.ts}")

    # Basic assertions
    assert len(alerts) > 0
    assert all(isinstance(alert, Alert) for alert in alerts)

====================================================
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any
import camelsnake  # Make sure to install this: pip install camelsnake

TIME_FORMAT_OUTPUT = "%Y-%m-%dT%H:%M:%SZ"  # Example format

@dataclass
class Alert:
    """
    Specifies attributes to be included in an alert
    """

    satellite_id: int
    severity: str
    component: str
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert alert as per reporting requirements with camelCase keys
        """
        raw_dict = asdict(self)
        raw_dict["timestamp"] = self.timestamp.strftime(TIME_FORMAT_OUTPUT)

        # Convert keys to camelCase using camelsnake
        camel_dict = {
            camelsnake.snake_to_camel(k): v for k, v in raw_dict.items()
        }
        return camel_dict

