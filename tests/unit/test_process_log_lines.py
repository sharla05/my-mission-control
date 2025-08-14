from datetime import datetime, timedelta
from io import StringIO
from typing import List

from my_mission_control.alerter.log_file_processor_v2 import _process_log_lines
from tests.utils.log_helper import make_log_line


class TestProcessingLogFileLines:
    """
    That various combination of data the can be present in the log file.
    Simulates a file-like object using StringIO, data populated from array of string representing log file lines.
    """

    def test_alert_triggered_with_sample_data(self):
        """Positive - both thermostat and battery alerts are triggered when value crosses threshold"""
        base_time = datetime(2018, 1, 1, 23, 1, 5, 1_000)

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

        alerts: List[dict] = _process_log_lines(StringIO("\n".join(lines)))

        assert len(alerts) == 2
        assert sum(alert["component"] == "TSTAT" for alert in alerts) == 1
        tstat_alert = next(alert for alert in alerts if alert["component"] == "TSTAT")
        assert tstat_alert["satelliteId"] == 1000
        assert tstat_alert["severity"] == "RED HIGH"
        assert tstat_alert["component"] == "TSTAT"
        assert tstat_alert["timestamp"] == "2018-01-01T23:01:38.001000Z"

        assert sum(alert["component"] == "BATT" for alert in alerts) == 1
        batt_alert = next(alert for alert in alerts if alert["component"] == "BATT")
        assert batt_alert["satelliteId"] == 1000
        assert batt_alert["severity"] == "RED LOW"
        assert batt_alert["component"] == "BATT"
        assert batt_alert["timestamp"] == "2018-01-01T23:01:09.521000Z"

    def test_battery_alert_triggered(self):
        """Positive - battery alert is triggered when value fall below threshold"""
        base_time = datetime(2025, 8, 13, 10, 0, 0, 521_000)

        # 3 battery readings for satellite 1001 below red_low_limit (8) within 5 minutes
        lines = [
            make_log_line(base_time, 1001, 17, 15, 9, 8, 7.5, "BATT"),
            make_log_line(base_time + timedelta(seconds=60), 1001, 27, 15, 9, 8, 7.2, "BATT"),
            make_log_line(base_time + timedelta(seconds=120), 1001, 27, 15, 9, 8, 7.8, "BATT"),
        ]

        alerts: List[dict] = _process_log_lines(StringIO("\n".join(lines)))

        assert len(alerts) == 1
        assert alerts[0]["satelliteId"] == 1001
        assert alerts[0]["severity"] == "RED LOW"
        assert alerts[0]["component"] == "BATT"
        assert alerts[0]["timestamp"] == "2025-08-13T10:00:00.521000Z"

    def test_no_battery_alert_less_than_three(self):
        """Negative - battery alert is not triggered for less than three threshold violation"""
        base_time = datetime(2025, 8, 13, 10, 0, 0, 521_000)

        # 2 battery readings for satellite 1001 below red_low_limit (8) within 5 minutes
        lines = [
            make_log_line(base_time, 1001, 17, 15, 9, 8, 7.5, "BATT"),
            make_log_line(base_time + timedelta(seconds=60), 1001, 27, 15, 9, 8, 7.2, "BATT"),
        ]

        alerts: List[dict] = _process_log_lines(StringIO("\n".join(lines)))

        assert len(alerts) == 0

    def test_thermostat_alert_triggered(self):
        """Positive - thermostat alert is triggered when values for three entries cross threshold"""
        base_time = datetime(2025, 8, 13, 11, 0, 0)

        # 3 thermostat readings for satellite 1002 exceeding red_high_limit (101) within 5 minutes
        lines = [
            make_log_line(base_time, 1002, 101, 98, 25, 20, 101.5, "TSTAT"),
            make_log_line(base_time + timedelta(seconds=30), 1002, 101, 98, 25, 20, 101.1, "TSTAT"),
            make_log_line(base_time + timedelta(seconds=60), 1002, 101, 98, 25, 20, 101.9, "TSTAT"),
        ]

        alerts: List[dict] = _process_log_lines(StringIO("\n".join(lines)))

        assert len(alerts) == 1
        assert alerts[0]["satelliteId"] == 1002
        assert alerts[0]["severity"] == "RED HIGH"
        assert alerts[0]["component"] == "TSTAT"
        assert alerts[0]["timestamp"] == "2025-08-13T11:00:00.000000Z"

    def test_no_thermostat_alert_less_than_three(self):
        """Negative - thermostat alert is not triggered when there are less than 3 values that cross threshold"""
        base_time = datetime(2025, 8, 13, 11, 0, 0)

        # 2 thermostat readings for satellite 1002 exceeding red_high_limit (101) within 5 minutes
        lines = [
            make_log_line(base_time, 1002, 101, 98, 25, 20, 101.5, "TSTAT"),
            make_log_line(base_time + timedelta(seconds=30), 1002, 101, 98, 25, 20, 101.1, "TSTAT"),
        ]

        alerts: List[dict] = _process_log_lines(StringIO("\n".join(lines)))

        assert len(alerts) == 0

    def test_battery_alert_with_more_than_three_entries(self):
        """Positive - battery alert is triggered when there are more than three values that cross threshold"""
        base_time = datetime(2025, 8, 13, 14, 0, 0)

        # Four battery readings for satellite 1001 below red_low_limit (8) within 5 minutes
        lines = [
            make_log_line(base_time, 1001, 17, 15, 9, 8, 7.5, "BATT"),
            make_log_line(base_time + timedelta(seconds=30), 1001, 17, 15, 9, 8, 7.2, "BATT"),
            make_log_line(base_time + timedelta(seconds=60), 1001, 17, 15, 9, 8, 7.8, "BATT"),
            make_log_line(base_time + timedelta(seconds=90), 1001, 17, 15, 9, 8, 7.1, "BATT"),  # Fourth entry
        ]

        alerts: List[dict] = _process_log_lines(StringIO("\n".join(lines)))

        assert len(alerts) == 1
        assert alerts[0]["satelliteId"] == 1001
        assert alerts[0]["severity"] == "RED LOW"
        assert alerts[0]["component"] == "BATT"
        assert alerts[0]["timestamp"] == "2025-08-13T14:00:00.000000Z"

    def test_thermostat_alert_with_more_than_three_entries(self):
        """Positive - thermostat alert is triggered when more than three values cross threshold"""
        base_time = datetime(2025, 8, 13, 11, 0, 0)

        # 3 thermostat readings for satellite 1002 exceeding red_high_limit (101) within 5 minutes
        lines = [
            make_log_line(base_time, 1002, 101, 98, 25, 20, 101.5, "TSTAT"),
            make_log_line(base_time + timedelta(seconds=30), 1002, 101, 98, 25, 20, 101.1, "TSTAT"),
            make_log_line(base_time + timedelta(seconds=60), 1002, 101, 98, 25, 20, 101.9, "TSTAT"),
            make_log_line(base_time + timedelta(seconds=120), 1002, 101, 98, 25, 20, 100.1, "TSTAT"),
        ]

        alerts: List[dict] = _process_log_lines(StringIO("\n".join(lines)))

        assert len(alerts) == 1
        assert alerts[0]["satelliteId"] == 1002
        assert alerts[0]["severity"] == "RED HIGH"
        assert alerts[0]["component"] == "TSTAT"
        assert alerts[0]["timestamp"] == "2025-08-13T11:00:00.000000Z"

    def test_two_consecutive_battery_alerts_triggered(self):
        """Positive - two battery alerts are triggered when set of violating values are more than 5 minutes a part"""
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

        alerts: List[dict] = _process_log_lines(StringIO("\n".join(lines)))

        assert len(alerts) == 2
        assert all(a["satelliteId"] == 1001 for a in alerts)
        assert all(a["severity"] == "RED LOW" for a in alerts)
        assert all(a["component"] == "BATT" for a in alerts)

        assert alerts[0]["timestamp"] == "2025-08-13T15:00:00.000000Z"
        assert alerts[1]["timestamp"] == "2025-08-13T15:06:00.000000Z"

    def test_two_consecutive_thermostat_alerts_triggered(self):
        """Positive - two thermostat alerts are triggered when set of violating values are more than 5 minutes a part"""
        base_time = datetime(2025, 8, 13, 11, 0, 0)

        # First set of three violations for satellite 1001
        lines = [
            make_log_line(base_time, 1001, 101, 98, 25, 20, 101.5, "TSTAT"),
            make_log_line(base_time + timedelta(seconds=30), 1001, 101, 98, 25, 20, 101.1, "TSTAT"),
            make_log_line(base_time + timedelta(seconds=60), 1001, 101, 98, 25, 20, 101.9, "TSTAT"),
            # Second set of three violations, starting after the first alert window
            make_log_line(base_time + timedelta(minutes=6), 1001, 101, 98, 25, 20, 101.1, "TSTAT"),
            make_log_line(base_time + timedelta(minutes=6, seconds=30), 1001, 101, 98, 25, 20, 101.2, "TSTAT"),
            make_log_line(base_time + timedelta(minutes=7), 1001, 101, 98, 25, 20, 101.3, "TSTAT"),
        ]

        alerts: List[dict] = _process_log_lines(StringIO("\n".join(lines)))

        assert len(alerts) == 2
        assert all(a["satelliteId"] == 1001 for a in alerts)
        assert all(a["severity"] == "RED HIGH" for a in alerts)
        assert all(a["component"] == "TSTAT" for a in alerts)

        assert alerts[0]["timestamp"] == "2025-08-13T11:00:00.000000Z"
        assert alerts[1]["timestamp"] == "2025-08-13T11:06:00.000000Z"

    def test_no_battery_alert_multiple_satellites(self):
        """Negative - no battery alert when 3 values from different satellites cross threshold with in 5 minutes window"""
        base_time = datetime(2025, 8, 13, 12, 0, 0)

        # Three readings below the red low limit(8), but for two different satellites
        lines = [
            make_log_line(base_time, 1001, 17, 15, 9, 8, 7.5, "BATT"),  # Satellite 1001
            make_log_line(base_time + timedelta(seconds=60), 1002, 17, 15, 9, 8, 7.2, "BATT"),  # Satellite 1002
            make_log_line(base_time + timedelta(seconds=120), 1001, 17, 15, 9, 8, 7.8, "BATT"),  # Satellite 1001
        ]

        alerts: List[dict] = _process_log_lines(StringIO("\n".join(lines)))

        assert len(alerts) == 0

    def test_no_thermostat_alert_multiple_satellites(self):
        """Negative -  no thermostat alert when 3 values from different satellites cross threshold with in 5 minutes window"""
        base_time = datetime(2025, 8, 13, 11, 0, 0)

        # 3 thermostat readings exceeding red_high_limit (101) within 5 minutes, but for two different satellites
        lines = [
            make_log_line(base_time, 1002, 101, 98, 25, 20, 101.5, "TSTAT"),
            make_log_line(base_time + timedelta(seconds=30), 1001, 101, 98, 25, 20, 101.1, "TSTAT"),
            make_log_line(base_time + timedelta(seconds=60), 1002, 101, 98, 25, 20, 101.9, "TSTAT"),
        ]

        alerts: List[dict] = _process_log_lines(StringIO("\n".join(lines)))

        assert len(alerts) == 0

    def test_no_battery_alert_readings_outside_time_window(self):
        """Negative -  no battery alert when 3 values cross threshold in more than 5 minutes window"""
        base_time = datetime(2025, 8, 13, 13, 0, 0)

        # Three readings, but the first one is too old (6 minutes ago) to be considered
        lines = [
            make_log_line(base_time, 1001, 17, 15, 9, 8, 7.5, "BATT"),
            make_log_line(base_time + timedelta(minutes=6), 1001, 17, 15, 9, 8, 7.2, "BATT"),  # This one resets the window
            make_log_line(base_time + timedelta(minutes=6, seconds=30), 1001, 17, 15, 9, 8, 7.8, "BATT"),
        ]

        alerts: List[dict] = _process_log_lines(StringIO("\n".join(lines)))

        assert len(alerts) == 0

    def test_no_thermostat_alert_readings_outside_time_window(self):
        """Negative -  no battery alert when 3 values cross threshold in more than 5 minutes window"""
        base_time = datetime(2025, 8, 13, 13, 0, 0)

        # Three readings, but the first one is too old (6 minutes ago) to be considered
        lines = [
            make_log_line(base_time, 1002, 101, 98, 25, 20, 101.5, "TSTAT"),
            make_log_line(base_time + timedelta(minutes=6), 1002, 101, 98, 25, 20, 101.1, "TSTAT"),
            make_log_line(base_time + timedelta(minutes=6, seconds=60), 1002, 101, 98, 25, 20, 101.9, "TSTAT"),
        ]

        alerts: List[dict] = _process_log_lines(StringIO("\n".join(lines)))

        assert len(alerts) == 0
