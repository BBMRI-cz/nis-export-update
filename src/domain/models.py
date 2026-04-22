from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PredictiveNumberStatus(Enum):
    SOURCE_NOT_FOUND = "source_not_found"
    READY_FOR_UPLOAD = "ready_for_upload"
    UPLOADED = "uploaded"
    UPLOAD_FAILED = "upload_failed"


@dataclass
class PredictiveNumberState:
    pseudo_pred_number: str
    real_pred_number: str
    status: PredictiveNumberStatus
    hash: str | None
    last_seen_at: datetime
    last_processed_at: datetime
    last_error: str | None
