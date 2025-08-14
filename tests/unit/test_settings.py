import importlib

import my_mission_control.config.settings as settings


# Test settings confirurable using environment variables
class TestEnvVarConfigurableSettings:
    def test_alert_defaults(self, monkeypatch):
        monkeypatch.delenv("ALERT_VIOLATION_COUNT_THRESHOLD", raising=False)
        monkeypatch.delenv("ALERT_VIOLATION_TIME_WINDOW_MINUTES", raising=False)
        importlib.reload(settings)
        assert settings.AlertCfg.ALERT_VIOLATION_COUNT_THRESHOLD == 3
        assert settings.AlertCfg.ALERT_VIOLATION_TIME_WINDOW_MINUTES == 5

    def test_alert_overrides(self, monkeypatch):
        monkeypatch.setenv("ALERT_VIOLATION_COUNT_THRESHOLD", "11")
        monkeypatch.setenv("ALERT_VIOLATION_TIME_WINDOW_MINUTES", "22")
        importlib.reload(settings)
        assert settings.AlertCfg.ALERT_VIOLATION_COUNT_THRESHOLD == 11
        assert settings.AlertCfg.ALERT_VIOLATION_TIME_WINDOW_MINUTES == 22

    def test_severity_defaults(self, monkeypatch):
        monkeypatch.delenv("SEVERITY_RED_HIGH", raising=False)
        monkeypatch.delenv("SEVERITY_RED_LOW", raising=False)
        importlib.reload(settings)
        assert settings.SeverityLevelCfg.RED_HIGH == "RED HIGH"
        assert settings.SeverityLevelCfg.RED_LOW == "RED LOW"

    def test_severity_overrides(self, monkeypatch):
        monkeypatch.setenv("SEVERITY_RED_HIGH", "RED HIGH OVERRIDE")
        monkeypatch.setenv("SEVERITY_RED_LOW", "RED LOW OVERRIDE")
        importlib.reload(settings)
        assert settings.SeverityLevelCfg.RED_HIGH == "RED HIGH OVERRIDE"
        assert settings.SeverityLevelCfg.RED_LOW == "RED LOW OVERRIDE"

    def test_log_delimiter(self, monkeypatch):
        monkeypatch.delenv("LOG_LINE_DELIMITER", raising=False)
        importlib.reload(settings)
        assert settings.LogCfg.LOG_LINE_DELIMITER == "|"

    def test_log_delimiter_overrides(self, monkeypatch):
        monkeypatch.setenv("LOG_LINE_DELIMITER", ";")
        importlib.reload(settings)
        assert settings.LogCfg.LOG_LINE_DELIMITER == ";"


# Test non-configurable settings
class NonConfigurableSettings:
    def test_non_configurable_values(self, monkeypatch):
        assert settings.LogCfg.LOG_LINE_EXPECTED_FIELD_COUNT == 8
        assert settings.LogCfg.LOG_LINE_TIME_FORMAT_INPUT == "%Y%m%d %H:%M:%S.%f"
        assert settings.LogCfg.LOG_LINE_COMPONENT_TSTAT == "TSTAT"
        assert settings.LogCfg.LOG_LINE_COMPONENT_BATT == "BATT"
        assert settings.AlertCfg.ALERT_TIME_FORMAT_OUTPUT == "%Y-%m-%dT%H:%M:%S.%fZ"
