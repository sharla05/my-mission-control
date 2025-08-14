from datetime import datetime, timedelta
from typing import Dict, Optional

import pytest

from my_mission_control.alerter.alert_strategy import AlertEvalStrategy
from my_mission_control.alerter.alert_tracker import TIME_DELTA, VIOLATION_THRESHOLD, AlertTracker
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
    Behavioral tests for the AlertTracker class.
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

    # --------------------------------------------------------------------------------------------------
    # New or Refactored Tests
    # --------------------------------------------------------------------------------------------------

    def test_no_alert_for_insufficient_violations(self, tracker):
        """
        Verifies that an alert is not returned when the number of violations
        is less than the VIOLATION_THRESHOLD.
        """
        base_time = datetime(2023, 1, 1, 12, 0, 0)

        # Process violations up to one less than the threshold
        for i in range(VIOLATION_THRESHOLD - 1):
            timestamp = base_time + timedelta(seconds=i)
            entry = self.make_log_entry(timestamp, 100)
            alert = tracker.process_log_entry(entry)
            assert alert is None, f"An alert was incorrectly returned on violation {i + 1}."

    def test_alert_triggered_at_threshold_within_time_window(self, tracker):
        """
        Verifies that an alert is returned exactly when the VIOLATION_THRESHOLD
        is met within the TIME_DELTA window.
        """
        base_time = datetime(2023, 1, 1, 12, 0, 0)

        # Process violations one by one
        alert = None
        for i in range(VIOLATION_THRESHOLD):
            timestamp = base_time + timedelta(seconds=i * 10)
            entry = self.make_log_entry(timestamp, 100)
            alert = tracker.process_log_entry(entry)

        # The last violation should trigger the alert
        assert alert is not None, "An alert was not triggered when the threshold was met."
        assert alert.violation_count == VIOLATION_THRESHOLD
        assert alert.component == "TEST_CMPNT"
        assert alert.sat_id == 1
        assert alert.timestamp == base_time

    def test_no_alert_when_violations_are_spread_out(self, tracker):
        """
        Verifies that an alert is not returned if the violations are spaced
        out beyond the TIME_DELTA window.
        """
        base_time = datetime(2023, 1, 1, 12, 0, 0)

        # Process a violation
        entry1 = self.make_log_entry(base_time, 100)
        tracker.process_log_entry(entry1)

        # Process a violation after the time window has expired
        entry2_ts = base_time + TIME_DELTA + timedelta(seconds=1)
        entry2 = self.make_log_entry(entry2_ts, 100)
        alert = tracker.process_log_entry(entry2)
        assert alert is None, "An alert was incorrectly triggered by spaced-out violations."

        # Process a third violation to confirm a new sequence starts
        entry3_ts = entry2_ts + timedelta(seconds=1)
        entry3 = self.make_log_entry(entry3_ts, 100)
        alert = tracker.process_log_entry(entry3)
        assert alert is None, "An alert was incorrectly triggered by a new sequence."

    def test_no_alert_retrigger_after_initial_alert(self, tracker):
        """
        Verifies that a new alert is not generated for additional violations
        that fall within the same time window as a previously triggered alert.
        """
        base_time = datetime(2023, 1, 1, 12, 0, 0)

        # Trigger the first alert with VIOLATION_THRESHOLD entries
        for i in range(VIOLATION_THRESHOLD):
            timestamp = base_time + timedelta(seconds=i * 10)
            entry = self.make_log_entry(timestamp, 100)
            tracker.process_log_entry(entry)

        # Add another violation just after the alert
        new_timestamp = base_time + timedelta(seconds=40)
        new_entry = self.make_log_entry(new_timestamp, 100)
        alert = tracker.process_log_entry(new_entry)

        # No new alert should be generated
        assert alert is None, "An alert was re-triggered for violations in the same time window."

    def test_alert_retrigger_after_time_window_elapses(self, tracker):
        """
        Verifies that a new alert can be triggered for a new set of violations
        after the time window of a previous alert has fully elapsed.
        """
        base_time = datetime(2023, 1, 1, 12, 0, 0)

        # Trigger the first alert
        for i in range(VIOLATION_THRESHOLD):
            timestamp = base_time + timedelta(seconds=i * 10)
            entry = self.make_log_entry(timestamp, 100)
            tracker.process_log_entry(entry)

        # Move forward in time past the alert's time window
        new_base_time = base_time + TIME_DELTA + timedelta(seconds=1)

        # Trigger a second alert with a new set of violations
        alert = None
        for i in range(VIOLATION_THRESHOLD):
            timestamp = new_base_time + timedelta(seconds=i * 10)
            entry = self.make_log_entry(timestamp, 100)
            alert = tracker.process_log_entry(entry)

        assert alert is not None, "A new alert was not triggered after the time window elapsed."
        assert alert.violation_count == VIOLATION_THRESHOLD
        assert alert.timestamp == new_base_time
