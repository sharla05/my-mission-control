import os

from my_mission_control.utils.utility import get_env_var_int


class AlertOutputCfg:
    SEVERITY_RED_HIGH = os.getenv("SEVERITY_RED_HIGH", "RED HIGH")
    SEVERITY_RED_LOW = os.getenv("SEVERITY_RED_LOW", "RED LOW")
    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class InputLogFileCfg:
    LOG_LINE_DELIMITER = os.getenv("LOG_LINE_DELIMITER", "|")

    LOG_LINE_INPUT_FORMAT = "<timestamp>|<satellite-id>|<red-high-limit>|<yellow-high-limit>|<yellow-low-limit>|<red-low-limit>|<raw-value>|<component>"
    LOG_LINE_EXPECTED_FIELD_COUNT = len(LOG_LINE_INPUT_FORMAT.split("|"))

    # Values from log file used in code, for parsing and determining alert strategy
    LOG_LINE_TIMESTAMP_FORMAT = "%Y%m%d %H:%M:%S.%f"
    LOG_LINE_COMPONENT_TSTAT = "TSTAT"
    LOG_LINE_COMPONENT_BATT = "BATT"


class AlertRuleCfg:
    ALERT_VIOLATION_COUNT_THRESHOLD: int = get_env_var_int("ALERT_VIOLATION_COUNT_THRESHOLD", 3)
    ALERT_VIOLATION_TIME_WINDOW_MINUTES: int = get_env_var_int("ALERT_VIOLATION_TIME_WINDOW_MINUTES", 5)
