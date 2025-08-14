from datetime import datetime, timedelta
from typing import Dict, Optional

import pytest

from my_mission_control.alerter.alert_strategy import AlertEvalStrategy, RedHighAlertStrategy, RedLowAlertStrategy
from my_mission_control.alerter.alert_tracker import AlertTracker
from my_mission_control.config.settings import AlertOutputCfg, InputLogFileCfg
from my_mission_control.entity.log_entry import LogEntry


class TestAlertStrategies:
    @pytest.fixture
    def base_time(self):
        return datetime(2018, 1, 1, 23, 1, 5)

    @pytest.fixture
    def red_high_limit(self):
        return 101

    @pytest.fixture
    def red_low_limit(self):
        return 8

    def make_log_entry_thermostat(self, ts: datetime, raw_value: float, rhl, rll) -> LogEntry:
        return LogEntry(ts, 1000, rhl, 0, 0, rll, float(raw_value), InputLogFileCfg.LOG_LINE_COMPONENT_TSTAT)

    def make_log_entry_battery(self, ts: datetime, raw_value: float, rhl, rll) -> LogEntry:
        return LogEntry(ts, 1000, rhl, 0, 0, rll, float(raw_value), InputLogFileCfg.LOG_LINE_COMPONENT_BATT)

    def test_alert_triggered_with_default_alert_strategy(self, base_time, red_high_limit, red_low_limit):
        alert_eval_strategy_map: Dict[str, AlertEvalStrategy] = {InputLogFileCfg.LOG_LINE_COMPONENT_BATT: RedLowAlertStrategy(), InputLogFileCfg.LOG_LINE_COMPONENT_TSTAT: RedHighAlertStrategy()}
        alert_tracker = AlertTracker(alert_eval_strategy_map)

        log_entries = [
            self.make_log_entry_thermostat(base_time + timedelta(seconds=10), red_high_limit + 0.1, red_high_limit, red_low_limit),
            self.make_log_entry_thermostat(base_time + timedelta(seconds=30), red_high_limit + 0.1, red_high_limit, red_low_limit),
            self.make_log_entry_thermostat(base_time + timedelta(seconds=60), red_high_limit + 0.1, red_high_limit, red_low_limit),
        ]

        # First violation
        alert = alert_tracker.process_log_entry(log_entries[0])
        assert alert is None
        # Second violation
        alert = alert_tracker.process_log_entry(log_entries[1])
        assert alert is None
        # Third violation
        alert = alert_tracker.process_log_entry(log_entries[0])
        assert alert is not None
        alert.satellite_id = 1000
        alert.severity = AlertOutputCfg.SEVERITY_RED_HIGH
        alert.component = InputLogFileCfg.LOG_LINE_COMPONENT_TSTAT
        alert.timestamp = base_time + timedelta(seconds=10)

    # Test replacing Evaluation Strategy in AlertTracker
    def test_alert_triggered_with_mock_alert_strategy(self, base_time, red_high_limit, red_low_limit):
        """Use Mock Strategy for threshold check"""
        MOCK_TRIGGER_VALUE: int = 999
        MOCK_SEVERITY = "MOCK SEVERITY"

        # Use a mock AlertEvalStrategy to control when a violation occurs.
        class MockAlertEvalStrategy(AlertEvalStrategy):
            def evaluate(self, log_entry: LogEntry) -> Optional[str]:
                # For our tests, we'll assume a violation occurs when the raw value is 100
                if log_entry.raw_value == MOCK_TRIGGER_VALUE:
                    return MOCK_SEVERITY
                return None

        alert_eval_strategy_map: Dict[str, AlertEvalStrategy] = {InputLogFileCfg.LOG_LINE_COMPONENT_BATT: MockAlertEvalStrategy(), InputLogFileCfg.LOG_LINE_COMPONENT_TSTAT: MockAlertEvalStrategy()}
        alert_tracker = AlertTracker(alert_eval_strategy_map)

        log_entries = [
            self.make_log_entry_thermostat(base_time + timedelta(seconds=10), red_high_limit + 0.1, red_high_limit, red_low_limit),
            self.make_log_entry_thermostat(base_time + timedelta(seconds=30), red_high_limit + 0.1, red_high_limit, red_low_limit),
            self.make_log_entry_thermostat(base_time + timedelta(seconds=60), red_high_limit + 0.1, red_high_limit, red_low_limit),
        ]

        # No violation of mock evaluation strategy
        alert = alert_tracker.process_log_entry(log_entries[0])
        assert alert is None
        alert = alert_tracker.process_log_entry(log_entries[1])
        assert alert is None
        alert = alert_tracker.process_log_entry(log_entries[0])
        assert alert is None

        log_entries = [
            self.make_log_entry_thermostat(base_time + timedelta(seconds=10), MOCK_TRIGGER_VALUE, 0, 0),
            self.make_log_entry_thermostat(base_time + timedelta(seconds=30), MOCK_TRIGGER_VALUE, 0, 0),
            self.make_log_entry_thermostat(base_time + timedelta(seconds=60), MOCK_TRIGGER_VALUE, 0, 0),
        ]

        # First violation
        alert = alert_tracker.process_log_entry(log_entries[0])
        assert alert is None
        # Second violation
        alert = alert_tracker.process_log_entry(log_entries[1])
        assert alert is None
        # Third violation
        alert = alert_tracker.process_log_entry(log_entries[0])
        assert alert is not None

        alert.satellite_id = 1000
        alert.severity = MOCK_SEVERITY
        alert.component = InputLogFileCfg.LOG_LINE_COMPONENT_TSTAT
        alert.timestamp = base_time + timedelta(seconds=10)
