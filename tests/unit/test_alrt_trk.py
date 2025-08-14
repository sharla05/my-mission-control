from datetime import datetime, timedelta
from typing import Dict, Optional
from unittest.mock import Mock

import pytest

from my_mission_control.alerter.alert_strategy import AlertEvalStrategy
from my_mission_control.alerter.alert_tracker import ALERT_VIOLATION_COUNT_THRESHOLD, TIME_DELTA, AlertTracker
from my_mission_control.entity.log_entry import LogEntry


# We'll use a mock AlertEvalStrategy to control when a violation occurs.
# This allows us to focus the test on the AlertTracker's logic.
class MockAlertEvalStrategy(AlertEvalStrategy):
    def evaluate(self, log_entry: LogEntry) -> Optional[str]:
        # For our tests, we'll assume a violation occurs when the raw value is 100
        if log_entry.raw_value == 100:
            return "RED"
        return None


class TestAlertTracker:
    """
    Unit tests for the AlertTracker class.
    """

    @pytest.fixture
    def tracker(self):
        """
        Fixture to create a new AlertTracker instance for each test.
        """
        alert_eval_strategy_map: Dict[str, AlertEvalStrategy] = {"TEST_CMPNT": MockAlertEvalStrategy()}
        return AlertTracker(alert_eval_strategy_map)

    def make_log_entry(self, timestamp: datetime, raw_value: int) -> LogEntry:
        """
        Helper function to create a simplified LogEntry for testing.
        """
        return LogEntry(timestamp=timestamp, satellite_id=1, component="TEST_CMPNT", raw_value=raw_value, red_high_limit=100, yellow_high_limit=90, yellow_low_limit=10, red_low_limit=5)

    def test_no_alert_for_single_violation(self, tracker):
        """
        Tests that a single violation does not trigger an alert.
        """
        timestamp = datetime(2023, 1, 1, 12, 0, 0)
        entry = self.make_log_entry(timestamp, 100)

        alert = tracker.process_log_entry(entry)

        assert alert is None
        assert len(tracker.alert_timestamps[1]["TEST_CMPNT"]) == 1

    def test_alert_triggered_after_threshold(self, tracker):
        """
        Tests that an alert is triggered exactly when the violation threshold is met.
        """
        base_time = datetime(2023, 1, 1, 12, 0, 0)

        # Process violations one by one, staying within the time window
        alerts = []
        for i in range(ALERT_VIOLATION_COUNT_THRESHOLD):
            timestamp = base_time + timedelta(seconds=i * 10)
            entry = self.make_log_entry(timestamp, 100)
            alert = tracker.process_log_entry(entry)
            if alert:
                alerts.append(alert)

        # The third violation should trigger an alert
        assert len(alerts) == 1
        assert alerts[0].violation_count == ALERT_VIOLATION_COUNT_THRESHOLD
        assert alerts[0].component == "TEST_CMPNT"
        assert alerts[0].timestamp == base_time

        # After the alert, the timestamps deque should contain all three entries
        assert len(tracker.alert_timestamps[1]["TEST_CMPNT"]) == ALERT_VIOLATION_COUNT_THRESHOLD

    def test_violations_expire_from_time_window(self, tracker):
        """
        Tests that old violations are correctly removed from the time window.
        """
        base_time = datetime(2023, 1, 1, 12, 0, 0)

        # First violation is added
        entry1 = self.make_log_entry(base_time, 100)
        tracker.process_log_entry(entry1)

        # A second violation occurs just outside the time window
        entry2 = self.make_log_entry(base_time + TIME_DELTA + timedelta(seconds=1), 100)
        tracker.process_log_entry(entry2)

        # The first entry should have been removed, so the deque size is 1
        timestamps = tracker.alert_timestamps[1]["TEST_CMPNT"]
        assert len(timestamps) == 1
        assert timestamps[0] == entry2.timestamp

    def test_no_alert_for_expired_violations(self, tracker):
        """
        Tests that no alert is triggered if violations are spread across a time window larger than TIME_DELTA.
        """
        base_time = datetime(2023, 1, 1, 12, 0, 0)

        # Three violations, but the first is outside the time window of the third
        entry1 = self.make_log_entry(base_time, 100)
        tracker.process_log_entry(entry1)

        entry2 = self.make_log_entry(base_time + timedelta(minutes=1), 100)
        tracker.process_log_entry(entry2)

        entry3_ts = base_time + TIME_DELTA + timedelta(minutes=1)
        entry3 = self.make_log_entry(entry3_ts, 100)

        alert = tracker.process_log_entry(entry3)

        assert alert is None
        # The first entry should have been popped, so only two remain
        assert len(tracker.alert_timestamps[1]["TEST_CMPNT"]) == 2

    def test_no_retrigger_alert_in_same_time_window(self, tracker):
        """
        Tests that a new alert is not generated for violations that fall within the same time window as a previous alert.
        """
        base_time = datetime(2023, 1, 1, 12, 0, 0)

        # Trigger the first alert with VIOLATION_THRESHOLD entries
        for i in range(ALERT_VIOLATION_COUNT_THRESHOLD):
            timestamp = base_time + timedelta(seconds=i * 10)
            entry = self.make_log_entry(timestamp, 100)
            tracker.process_log_entry(entry)

        # Verify first alert was triggered
        assert len(tracker.last_alert_timestamp[1]["TEST_CMPNT"]) > 0

        # Add another violation just after the alert
        new_timestamp = base_time + timedelta(seconds=40)
        new_entry = self.make_log_entry(new_timestamp, 100)
        alert = tracker.process_log_entry(new_entry)

        # No new alert should be generated, as the violation is within the same time window
        assert alert is None
