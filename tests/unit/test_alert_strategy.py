from datetime import datetime

import pytest

from my_mission_control.alerter.alert_strategy import RedHighAlertStrategy, RedLowAlertStrategy
from my_mission_control.config.settings import AlertOutputCfg
from my_mission_control.entity.log_entry import LogEntry


@pytest.fixture
def base_log_entry():
    return LogEntry(timestamp=datetime(2025, 8, 7, 19, 46, 0), satellite_id=1000, red_high_limit=100, yellow_high_limit=70, yellow_low_limit=30, red_low_limit=40, raw_value=50, component="DUMMY")


def test_red_low_alert_triggered(base_log_entry):
    strategy = RedLowAlertStrategy()
    base_log_entry.raw_value = base_log_entry.red_low_limit - 1  # Below red_low_limit
    assert strategy.evaluate(base_log_entry) == AlertOutputCfg.SEVERITY_RED_LOW


def test_red_low_alert_not_triggered(base_log_entry):
    strategy = RedLowAlertStrategy()
    base_log_entry.raw_value = base_log_entry.red_low_limit + 1  # Above red_low_limit
    assert strategy.evaluate(base_log_entry) is None


def test_red_high_alert_triggered(base_log_entry):
    strategy = RedHighAlertStrategy()
    base_log_entry.raw_value = base_log_entry.red_high_limit + 1  # Above red_high_limit
    assert strategy.evaluate(base_log_entry) == AlertOutputCfg.SEVERITY_RED_HIGH


def test_red_high_alert_not_triggered(base_log_entry):
    strategy = RedHighAlertStrategy()
    base_log_entry.raw_value = base_log_entry.red_high_limit - 1  # Below red_high_limit
    assert strategy.evaluate(base_log_entry) is None
