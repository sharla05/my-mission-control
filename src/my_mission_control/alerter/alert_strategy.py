"""
Alert evaluation strategies for log entries.

Implements the Strategy Pattern to support flexible and extensible alert evaluation logic.
"""

from abc import ABC
from typing import Optional

from my_mission_control.config.settings import AlertOutputCfg
from my_mission_control.entity.log_entry import LogEntry


class AlertEvalStrategy(ABC):
    """
    Abstract base for alert evaluation strategy.
        Extend this class to implement custom alert evaluation for the log entry
    """

    def evaluate(self, log_entry: LogEntry) -> Optional[str]:
        pass


class RedLowAlertStrategy(AlertEvalStrategy):
    """
    Evaluates whether a log entry value is below red-low-limit
    """

    def evaluate(self, log_entry: LogEntry) -> Optional[str]:
        """
        Returns 'RED LOW' if condition is met
        """
        if log_entry.raw_value < log_entry.red_low_limit:
            return AlertOutputCfg.SEVERITY_RED_LOW
        return None


class RedHighAlertStrategy(AlertEvalStrategy):
    """
    Evaluates whether a log entry value is abor red-high-limit
    """

    def evaluate(self, log_entry: LogEntry) -> Optional[str]:
        """
        Returns 'RED HIGH' if condition is met
        """
        if log_entry.raw_value > log_entry.red_high_limit:
            return AlertOutputCfg.SEVERITY_RED_HIGH
        return None
