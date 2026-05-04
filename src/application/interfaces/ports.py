from typing import Protocol

from domain.models import PatientAggregate, PlannedOperation, SyncState


class SourceDataGateway(Protocol):
    def fetch_patients(self) -> list[dict]: ...

    def fetch_radiology(self, accession_numbers: list[str]) -> list[dict]: ...

    def fetch_sequencing(self, predictive_number: str) -> dict | None: ...

    def fetch_wsi(self, bioptic_number: str) -> dict | None: ...


class CatalogueGateway(Protocol):
    def upsert_patient(self, patient: PatientAggregate) -> str: ...

    def delete_patient(self, entity_key: str, remote_id: str | None) -> None: ...


class SyncStateRepository(Protocol):
    def get(self, entity_type: str, entity_key: str) -> SyncState | None: ...

    def save(self, state: SyncState) -> None: ...

    def mark_missing_as_deleted(
        self, entity_type: str, seen_keys: set[str], run_id: str
    ) -> list[SyncState]: ...


class SyncPlanner(Protocol):
    def plan_patient(
        self, patient: PatientAggregate, current: SyncState | None
    ) -> PlannedOperation: ...
