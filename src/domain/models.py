from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json


class SyncStatus(Enum):
    PENDING = "pending"
    SYNCED = "synced"
    FAILED = "failed"
    DELETED = "deleted"


class CatalogueOperation(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SKIP = "skip"


@dataclass(frozen=True)
class SequencingData:
    predictive_number: str
    source_id: str
    payload: dict


@dataclass(frozen=True)
class WsiData:
    bioptic_number: str
    source_id: str
    payload: dict


@dataclass(frozen=True)
class RadiologyData:
    accession_number: str
    source_id: str
    payload: dict


@dataclass(frozen=True)
class Sample:
    sample_id: str
    predictive_number: str | None
    bioptic_number: str | None
    payload: dict
    sequencing: SequencingData | None = None
    wsi: WsiData | None = None


@dataclass(frozen=True)
class PatientAggregate:
    patient_id: str
    accession_numbers: list[str]
    samples: list[Sample]
    payload: dict
    radiology: list[RadiologyData]

    def is_upload_eligible(self) -> bool:
        return len(self.samples) > 0

    def source_fingerprint(self) -> str:
        serialized = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass
class SyncState:
    entity_type: str
    entity_key: str
    source_fingerprint: str
    catalogue_remote_id: str | None
    status: SyncStatus
    is_deleted: bool
    last_seen_at: datetime
    last_synced_at: datetime | None
    last_error: str | None
    run_id: str


@dataclass(frozen=True)
class PlannedOperation:
    entity_type: str
    entity_key: str
    operation: CatalogueOperation
    payload: dict | None
    source_fingerprint: str | None


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
