from datetime import datetime, timedelta
from typing import Dict, List, Optional

from my_mission_control.alerter.alert_rules import COMPONENT_BATT, COMPONENT_TSTAT
from my_mission_control.alerter.alert_strategy import AlertEvalStrategy, RedHighAlertStrategy, RedLowAlertStrategy
from my_mission_control.alerter.alert_tracker import AlertTracker
from my_mission_control.alerter.log_file_processor_v2 import _process_log_line
from my_mission_control.entity.alert import Alert
from tests.utils.log_helper import format_ts, make_log_line


class TestLogLineProcessing:
    """ """

    def setup_method(self):
        """ """
        alert_eval_strategy_map: Dict[str, AlertEvalStrategy] = {COMPONENT_BATT: RedLowAlertStrategy(), COMPONENT_TSTAT: RedHighAlertStrategy()}
        self.alert_tracker = AlertTracker(alert_eval_strategy_map)
        print("")

    def test_alert_triggered_with_sample_data(self):
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

        alerts: List[dict] = []
        # Process each log line individually and collect any generated alerts
        for line in lines:
            alert: Optional[Alert] = _process_log_line(line, self.alert_tracker)
            if alert:
                alerts.append(alert.to_dict())

        # Assertions
        assert len(alerts) == 2, "Expected exactly one alert to be triggered"

    def test_battery_alert_triggered(self):
        """Positive - battery"""
        base_time = datetime(2025, 8, 13, 10, 0, 0)

        # 3 battery readings for satellite 1001 below red_low_limit (8) within 5 minutes
        lines = [
            make_log_line(base_time, 1001, 17, 15, 9, 8, 7.5, "BATT"),
            make_log_line(base_time + timedelta(seconds=60), 1001, 27, 15, 9, 8, 7.2, "BATT"),
            make_log_line(base_time + timedelta(seconds=120), 1001, 27, 15, 9, 8, 7.8, "BATT"),
        ]
        print("")

        alerts: List[dict] = []
        for line in lines:
            alert: Optional[Alert] = _process_log_line(line, self.alert_tracker)
            if alert:
                print("alert", alert)
                alerts.append(alert.to_dict())

        assert len(alerts) == 1, "Expected one battery alert to be triggered"
        assert alerts[0]["component"] == "BATT", "Alert should be for battery"
        assert alerts[0]["satelliteId"] == 1001, "Alert should be for satellite 1001"

    def test_thermostat_alert_triggered(self):
        """Positive - temperature"""
        base_time = datetime(2025, 8, 13, 11, 0, 0)

        # 3 thermostat readings for satellite 1002 exceeding red_high_limit (101) within 5 minutes
        lines = [
            make_log_line(base_time, 1002, 101, 98, 25, 20, 101.5, "TSTAT"),
            make_log_line(base_time + timedelta(seconds=30), 1002, 101, 98, 25, 20, 101.1, "TSTAT"),
            make_log_line(base_time + timedelta(seconds=60), 1002, 101, 98, 25, 20, 101.9, "TSTAT"),
        ]

        alerts: List[dict] = []
        for line in lines:
            alert: Optional[Alert] = _process_log_line(line, self.alert_tracker)
            if alert:
                alerts.append(alert.to_dict())

        assert len(alerts) == 1, "Expected one thermostat alert to be triggered"
        assert alerts[0]["component"] == "TSTAT", "Alert should be for thermostat"
        assert alerts[0]["satelliteId"] == 1002, "Alert should be for satellite 1002"

    def test_alert_with_more_than_three_entries(self):
        """Positive"""
        base_time = datetime(2025, 8, 13, 14, 0, 0)

        # Four battery readings for satellite 1001 below red_low_limit within 5 minutes
        lines = [
            make_log_line(base_time, 1001, 17, 15, 9, 8, 7.5, "BATT"),
            make_log_line(base_time + timedelta(seconds=30), 1001, 17, 15, 9, 8, 7.2, "BATT"),
            make_log_line(base_time + timedelta(seconds=60), 1001, 17, 15, 9, 8, 7.8, "BATT"),
            make_log_line(base_time + timedelta(seconds=90), 1001, 17, 15, 9, 8, 7.1, "BATT"),  # Fourth entry
        ]

        alerts: List[dict] = []
        for line in lines:
            alert: Optional[Alert] = _process_log_line(line, self.alert_tracker)
            if alert:
                alerts.append(alert.to_dict())

        assert len(alerts) == 1, "Expected exactly one alert to be triggered, not a new one for the fourth entry"
        assert alerts[0]["component"] == "BATT", "Alert should be for battery"
        assert alerts[0]["satelliteId"] == 1001, "Alert should be for satellite 1001"

    def test_two_consecutive_alerts_triggered(self):
        """Positive"""
        base_time = datetime(2025, 8, 13, 15, 0, 0)

        # First set of three violations for satellite 1001
        lines = [
            make_log_line(base_time, 1001, 17, 15, 9, 8, 7.5, "BATT"),
            make_log_line(base_time + timedelta(seconds=30), 1001, 17, 15, 9, 8, 7.2, "BATT"),
            make_log_line(base_time + timedelta(seconds=60), 1001, 17, 15, 9, 8, 7.8, "BATT"),  # First alert triggered here
            # Second set of three violations, starting after the first alert window
            make_log_line(base_time + timedelta(minutes=6), 1001, 17, 15, 9, 8, 7.1, "BATT"),
            make_log_line(base_time + timedelta(minutes=6, seconds=30), 1001, 17, 15, 9, 8, 7.0, "BATT"),
            make_log_line(base_time + timedelta(minutes=7), 1001, 17, 15, 9, 8, 7.3, "BATT"),  # Second alert triggered here
        ]

        alerts: List[dict] = []
        for line in lines:
            alert: Optional[Alert] = _process_log_line(line, self.alert_tracker)
            if alert:
                alerts.append(alert.to_dict())

        assert len(alerts) == 2, "Expected two separate alerts to be triggered"
        assert all(a["component"] == "BATT" for a in alerts), "Both alerts should be for battery"
        assert all(a["satelliteId"] == 1001 for a in alerts), "Both alerts should be for satellite 1001"

    def test_no_alert_multiple_satellites(self):
        """Negative"""
        base_time = datetime(2025, 8, 13, 12, 0, 0)

        # Three readings below the red low limit, but for two different satellites
        lines = [
            make_log_line(base_time, 1001, 17, 15, 9, 8, 7.5, "BATT"),  # Satellite 1001
            make_log_line(base_time + timedelta(seconds=60), 1002, 17, 15, 9, 8, 7.2, "BATT"),  # Satellite 1002
            make_log_line(base_time + timedelta(seconds=120), 1001, 17, 15, 9, 8, 7.8, "BATT"),  # Satellite 1001
        ]

        alerts: List[dict] = []
        for line in lines:
            alert: Optional[Alert] = _process_log_line(line, self.alert_tracker)
            if alert:
                alerts.append(alert.to_dict())

        assert len(alerts) == 0, "No alert should be triggered with readings from different satellites"

    def test_no_alert_readings_outside_time_window(self):
        base_time = datetime(2025, 8, 13, 13, 0, 0)

        # Three readings, but the first one is too old (6 minutes ago) to be considered
        lines = [
            make_log_line(base_time, 1001, 17, 15, 9, 8, 7.5, "BATT"),
            make_log_line(base_time + timedelta(minutes=6), 1001, 17, 15, 9, 8, 7.2, "BATT"),  # This one resets the window
            make_log_line(base_time + timedelta(minutes=6, seconds=30), 1001, 17, 15, 9, 8, 7.8, "BATT"),
        ]

        alerts: List[dict] = []
        for line in lines:
            alert: Optional[Alert] = _process_log_line(line, self.alert_tracker)
            if alert:
                alerts.append(alert.to_dict())

        assert len(alerts) == 0, "No alert should be triggered when readings are outside the 5-minute window"

        # def test_alert_triggered_for_batt(self):
        #     """
        #     Tests that a RED_LOW alert is correctly triggered for the BATT component.
        #     """
        #     base_time = datetime(2025, 8, 7, 19, 0, 0)

        #     # These three lines all have a raw_value below the red_low threshold (5.0)
        #     # The third line should trigger the alert because it's the 3rd violation
        #     lines = [
        #         make_log_line(base_time, 1002, 90, 10, 5, 0, 4.9, "BATT"),
        #         make_log_line(base_time + timedelta(minutes=1), 1002, 90, 10, 5, 0, 4.8, "BATT"),
        #         make_log_line(base_time + timedelta(minutes=2), 1002, 90, 10, 5, 0, 4.7, "BATT"),
        #     ]

        #     alerts: List[dict] = []
        #     # Process each log line individually and collect any generated alerts
        #     for line in lines:
        #         alert: Optional[Alert] = _process_log_line(line, self.alert_tracker)
        #         if alert:
        #             alerts.append(alert.to_dict())

        #     # Assertions
        #     assert len(alerts) == 1, "Expected exactly one alert to be triggered"

        #     triggered_alert = alerts[0]

        #     assert triggered_alert["component"] == "BATT"
        #     assert triggered_alert["type"] == "RED_LOW"
        #     assert triggered_alert["violation_count"] == 3
        #     # Use timedelta to allow for slight precision differences
        #     assert triggered_alert["timestamp"] == format_ts(base_time + timedelta(minutes=2))

        # def test_no_alert_triggered_for_batt(self):
        #     """
        #     Tests that no alert is triggered when the raw_value is within the limits.
        #     """
        #     base_time = datetime(2025, 8, 7, 19, 0, 0)

        #     lines = [
        #         make_log_line(base_time, 1002, 90, 10, 5, 0, 5.1, "BATT"),
        #         make_log_line(base_time + timedelta(minutes=1), 1002, 90, 10, 5, 0, 5.0, "BATT"),
        #         make_log_line(base_time + timedelta(minutes=2), 1002, 90, 10, 5, 0, 5.2, "BATT"),
        #     ]

        #     alerts = []
        #     for line in lines:
        #         alert: Optional[Alert] = _process_log_line(line, self.alert_tracker)
        #         if alert:
        #             alerts.append(alert)

        #     assert len(alerts) == 0, "Expected no alerts to be triggered"


# ===============================================================================================================
# def test_alert_triggered_for_batt():
#     """
#     Tests that a RED_LOW alert is correctly triggered for the BATT component.
#     """
#     base_time = datetime(2025, 8, 7, 19, 0, 0)

#     # These three lines all have a raw_value below the red_low threshold (5.0)
#     # The third line should trigger the alert because it's the 3rd violation
#     lines = [
#         make_log_line(base_time, 1002, 90, 10, 5, 0, 4.9, "BATT"),
#         make_log_line(base_time + timedelta(minutes=1), 1002, 90, 10, 5, 0, 4.8, "BATT"),
#         make_log_line(base_time + timedelta(minutes=2), 1002, 90, 10, 5, 0, 4.7, "BATT"),
#     ]

#     alerts: List[dict] = []

#     # Map each component to its corresponding alert evaluation strategy
#     alert_eval_strategy_map: Dict[str, AlertEvalStrategy] = {COMPONENT_BATT: RedLowAlertStrategy(), COMPONENT_TSTAT: RedHighAlertStrategy()}
#     # Initialize the alert tracker with alert evaluation stragegy mapping
#     alert_tracker = AlertTracker(alert_eval_strategy_map)
#     # Process each log line individually and collect any generated alerts
#     for line in lines:
#         alert: Optional[Alert] = _process_log_line(line, alert_tracker)
#         if alert:
#             alerts.append(alert.to_dict())

#     # Assertions
#     assert len(alerts) == 1, "Expected exactly one alert to be triggered"

#     triggered_alert = alerts[0]

#     assert triggered_alert["component"] == "BATT"
#     assert triggered_alert["type"] == "RED_LOW"
#     assert triggered_alert["violation_count"] == 3
#     # Use timedelta to allow for slight precision differences
#     assert triggered_alert["timestamp"] == format_ts(base_time + timedelta(minutes=2))

# def test_no_alert_triggered_for_batt():
#     """
#     Tests that no alert is triggered when the raw_value is within the limits.
#     """
#     base_time = datetime(2025, 8, 7, 19, 0, 0)

#     lines = [
#         make_log_line(base_time, 1002, 90, 10, 5, 0, 5.1, "BATT"),
#         make_log_line(base_time + timedelta(minutes=1), 1002, 90, 10, 5, 0, 5.0, "BATT"),
#         make_log_line(base_time + timedelta(minutes=2), 1002, 90, 10, 5, 0, 5.2, "BATT"),
#     ]

#     alerts = []
#     for line in lines:
#         alert = _process_log_line(line)
#         if alert:
#             alerts.append(alert)

#     assert len(alerts) == 0, "Expected no alerts to be triggered"
