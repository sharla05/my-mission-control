"""
Dataclass for representing alerts
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict

from structlog.stdlib import get_logger

TIME_FORMAT_OUTPUT = "%Y-%m-%dT%H:%M:%S.%fZ"


logger = get_logger(__name__)


@dataclass
class Alert:
    """
    Specifies attributes to be included in an alert
    """

    satelliteId: int
    severity: str
    component: str
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert alert as per reporting requirements
        """
        alert_dict = asdict(self)
        alert_dict["timestamp"] = self.timestamp.strftime(TIME_FORMAT_OUTPUT)
        return alert_dict

    def to_json(self) -> str:
        """
        Serializes alert to a JSON string
        """
        return json.dumps(self.to_dict())
