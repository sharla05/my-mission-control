"""
Dataclass for representing a parsed log entry with satellite telemetry values.
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class LogEntry:
    """
    Represents a parsed log entry containing telemetry data for a satellite component,
    alert thresholds, and timestamp.

    Attributes:
        timestamp: Timestamp of the log entry.
        satellite_id: Satellite identifier.
        red_high_limit: Red high limit threshold.
        yellow_high_limit: Yellow high limit threshold.
        yellow_low_limit: Yellow low limit threshold.
        red_low_limit: Red low limit threshold.
        raw_value: Raw sensor measurement value.
        component: Component identifier.
    """

    timestamp: datetime
    satellite_id: int
    red_high_limit: int
    yellow_high_limit: int
    yellow_low_limit: int
    red_low_limit: int
    raw_value: float
    component: str
