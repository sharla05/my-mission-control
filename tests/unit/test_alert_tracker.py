from datetime import datetime, timedelta
from typing import Dict, List, Optional
from unittest.mock import patch

from my_mission_control.alerter.alert_rules import COMPONENT_BATT, COMPONENT_TSTAT
from my_mission_control.alerter.alert_strategy import AlertEvalStrategy, RedHighAlertStrategy, RedLowAlertStrategy
from my_mission_control.alerter.alert_tracker import AlertTracker
from my_mission_control.alerter.log_file_processor_v2 import _process_log_line
from my_mission_control.entity.alert import Alert
from tests.utils.log_helper import make_log_line


# @patch("my_mission_control.alerter.alert_tracker.evaluate_alert_condition", return_value="RED LOW")
# def test_alert_triggered_for_batt(mock_eval):
def test_alert_triggered_for_batt():
    alert_eval_strategy_map: Dict[str, AlertEvalStrategy] = {COMPONENT_BATT: RedLowAlertStrategy(), COMPONENT_TSTAT: RedHighAlertStrategy()}
    alert_tracker = AlertTracker(alert_eval_strategy_map)
    base_time = datetime(2025, 8, 7, 19, 0, 0)

    lines = [
        make_log_line(base_time, 1002, 90, 10, 5, 10, 9.0, "BATT"),
        make_log_line(base_time + timedelta(minutes=1), 1002, 90, 10, 5, 10, 9.8, "BATT"),
        make_log_line(base_time + timedelta(minutes=2), 1002, 90, 10, 5, 10, 9.7, "BATT"),
    ]

    alerts: List[dict] = []
    # Process each log line individually and collect any generated alerts
    for line in lines:
        alert: Optional[Alert] = _process_log_line(line, alert_tracker)
        if alert:
            alerts.append(alert.to_dict())

    # Assertions
    assert len(alerts) == 1, "Expected exactly one alert to be triggered"


# from datetime import datetime, timedelta
# from unittest.mock import patch

# from my_mission_control.alerter.alert_tracker import AlertTracker


# from alert.parser.parser import format_ts, make_log_line  # Or redefine locally if needed

# @patch("my_mission_control.alerter.alert_tracker.evaluate_alert_condition")
# def test_alert_tracker_with_sample_data(mock_eval):
#     # Mock severity based on component
#     def mock_severity(log_entry):
#         return "RED HIGH" if log_entry.cmpnt == "TSTAT" else "RED LOW"
#     mock_eval.side_effect = mock_severity

#     tracker = AlertTracker()
#     base_time = datetime(2018, 1, 1, 23, 1, 5)

#     lines = [
#         make_log_line(base_time, 1001, 101, 98, 25, 20, 99.9, "TSTAT"),
#         make_log_line(base_time + timedelta(seconds=4.52), 1000, 17, 15, 9, 8, 7.8, "BATT"),
#         make_log_line(base_time + timedelta(seconds=21.01), 1001, 101, 98, 25, 20, 99.8, "TSTAT"),
#         make_log_line(base_time + timedelta(seconds=33.0), 1000, 101, 98, 25, 20, 102.9, "TSTAT"),
#         make_log_line(base_time + timedelta(seconds=44.02), 1000, 101, 98, 25, 20, 87.9, "TSTAT"),
#         make_log_line(base_time + timedelta(seconds=64.01), 1001, 101, 98, 25, 20, 89.3, "TSTAT"),
#         make_log_line(base_time + timedelta(seconds=65.02), 1001, 101, 98, 25, 20, 89.4, "TSTAT"),
#         make_log_line(base_time + timedelta(seconds=66.3), 1000, 17, 15, 9, 8, 7.7, "BATT"),
#         make_log_line(base_time + timedelta(seconds=118.0), 1000, 101, 98, 25, 20, 102.7, "TSTAT"),
#         make_log_line(base_time + timedelta(seconds=120.0), 1000, 101, 98, 25, 20, 101.2, "TSTAT"),
#         make_log_line(base_time + timedelta(seconds=181.01), 1001, 101, 98, 25, 20, 89.9, "TSTAT"),
#         make_log_line(base_time + timedelta(seconds=186.53), 1000, 17, 15, 9, 8, 7.9, "BATT"),
#         make_log_line(base_time + timedelta(seconds=240.02), 1001, 101, 98, 25, 20, 89.9, "TSTAT"),
#         make_log_line(base_time + timedelta(seconds=242.42), 1001, 17, 15, 9, 8, 7.9, "BATT"),
#     ]

#     log_entries = parse_log_lines_to_json(lines)

#     alerts = []
#     for entry in log_entries:
#         alert = tracker.process_log_entry(entry)
#         if alert:
#             alerts.append(alert)

#     # Print alerts for inspection
#     for alert in alerts:
#         print(f"ALERT: sat_id={alert.sat_id}, cmpnt={alert.cmpnt}, severity={alert.severity}, ts={alert.ts}")

#     # Basic assertions
#     assert len(alerts) > 0
#     assert all(isinstance(alert, Alert) for alert in alerts)
