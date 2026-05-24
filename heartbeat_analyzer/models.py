from datetime import datetime
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, root_validator

# HeartbeatStatus defines the allowed status values for each heartbeat record.
# We use an enum so validation is explicit and invalid values can be handled.
class HeartbeatStatus(str, Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    UNKNOWN = "UNKNOWN"

# HeartbeatRecord is the model for one heartbeat log entry.
# Pydantic will validate incoming data, convert types, and support default values.
class HeartbeatRecord(BaseModel):
    timestamp: datetime
    instrument_id: str
    status: HeartbeatStatus
    message: str
    detail: Dict[str, Any] = {}

    @root_validator(pre=True)
    def normalize_status(cls, values):
        """Normalize unknown status values to UNKNOWN before validation."""
        raw_status = values.get("status")
        if raw_status not in HeartbeatStatus.__members__:
            values["status"] = HeartbeatStatus.UNKNOWN
        return values

   