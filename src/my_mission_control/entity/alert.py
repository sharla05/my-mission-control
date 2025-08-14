"""
Dataclass for representing alerts
"""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict

from structlog.stdlib import get_logger

from my_mission_control.config.settings import AlertCfg
from my_mission_control.utils.utility import snake_to_camel

logger = get_logger(__name__)


@dataclass
class Alert:
    """
    Specifies attributes to be included in an alert
    """

    satellite_id: int
    severity: str
    component: str
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert alert as per reporting requirements
        """
        raw_dict = asdict(self)
        raw_dict["timestamp"] = self.timestamp.strftime(AlertCfg.ALERT_TIME_FORMAT_OUTPUT)

        camel_dict = {snake_to_camel(k): v for k, v in raw_dict.items()}
        return camel_dict

    def to_json(self) -> str:
        """
        Serializes alert to a JSON string
        """
        return json.dumps(self.to_dict())
