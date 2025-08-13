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
        ts: Timestamp of the log entry.
        sat_id: Satellite identifier.
        rhl: Red high limit threshold.
        yhl: Yellow high limit threshold.
        yll: Yellow low limit threshold.
        rll: Red low limit threshold.
        val: Raw sensor measurement value.
        cmpnt: Component name.
    """

    ts: datetime
    sat_id: int
    rhl: int
    yhl: int
    yll: int
    rll: int
    val: float
    cmpnt: str
