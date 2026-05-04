from __future__ import annotations

from dataclasses import dataclass
import uuid

from application.interfaces.ports import (
    CatalogueGateway,
    SourceDataGateway,
    SyncPlanner,
    SyncStateRepository,
)
from domain.models import (
    CatalogueOperation,
    PatientAggregate,
    RadiologyData,
    Sample,
    SequencingData,
    SyncState,
    SyncStatus,
    WsiData,
    now_utc,
)


@dataclass
class RunSummary:
    run_id: str
    scanned: int = 0
    changed: int = 0
    uploaded: int = 0
    deleted: int = 0
    skipped: int = 0
    failed: int = 0


class CatalogueSyncService:
    def __init__(
        self,
        source_gateway: SourceDataGateway,
        catalogue_gateway: CatalogueGateway,
        state_repository: SyncStateRepository,
        planner: SyncPlanner,
    ) -> None:
        self.source_gateway = source_gateway
        self.catalogue_gateway = catalogue_gateway
        self.state_repository = state_repository
        self.planner = planner

    def run_catalogue_sync(self) -> RunSummary:
        run_id = str(uuid.uuid4())
        summary = RunSummary(run_id=run_id)
        raw_patients = self.source_gateway.fetch_patients()

        seen_keys: set[str] = set()
        for raw_patient in raw_patients:
            patient = self._build_patient_aggregate(raw_patient)
            summary.scanned += 1
            seen_keys.add(patient.patient_id)

            existing = self.state_repository.get("patient", patient.patient_id)
            operation = self.planner.plan_patient(patient, existing)
            if operation.operation == CatalogueOperation.SKIP:
                summary.skipped += 1
                continue

            summary.changed += 1
            try:
                if operation.operation in (
                    CatalogueOperation.CREATE,
                    CatalogueOperation.UPDATE,
                ):
                    remote_id = self.catalogue_gateway.upsert_patient(patient)
                    summary.uploaded += 1
                    self.state_repository.save(
                        SyncState(
                            entity_type="patient",
                            entity_key=patient.patient_id,
                            source_fingerprint=operation.source_fingerprint or "",
                            catalogue_remote_id=remote_id,
                            status=SyncStatus.SYNCED,
                            is_deleted=False,
                            last_seen_at=now_utc(),
                            last_synced_at=now_utc(),
                            last_error=None,
                            run_id=run_id,
                        )
                    )
            except Exception as exc:  # prototype: keep run moving
                summary.failed += 1
                self.state_repository.save(
                    SyncState(
                        entity_type="patient",
                        entity_key=patient.patient_id,
                        source_fingerprint=operation.source_fingerprint or "",
                        catalogue_remote_id=existing.catalogue_remote_id
                        if existing
                        else None,
                        status=SyncStatus.FAILED,
                        is_deleted=False,
                        last_seen_at=now_utc(),
                        last_synced_at=existing.last_synced_at if existing else None,
                        last_error=str(exc),
                        run_id=run_id,
                    )
                )

        missing_states = self.state_repository.mark_missing_as_deleted(
            entity_type="patient", seen_keys=seen_keys, run_id=run_id
        )
        for state in missing_states:
            try:
                self.catalogue_gateway.delete_patient(
                    state.entity_key, state.catalogue_remote_id
                )
                summary.deleted += 1
            except Exception:
                summary.failed += 1

        return summary

    def _build_patient_aggregate(self, raw_patient: dict) -> PatientAggregate:
        samples: list[Sample] = []
        for raw_sample in raw_patient.get("samples", []):
            predictive_number = raw_sample.get("predictive_number")
            bioptic_number = raw_sample.get("bioptic_number")

            sequencing = None
            if predictive_number:
                sequencing_payload = self.source_gateway.fetch_sequencing(
                    predictive_number
                )
                if sequencing_payload:
                    sequencing = SequencingData(
                        predictive_number=predictive_number,
                        source_id=str(sequencing_payload.get("id", predictive_number)),
                        payload=sequencing_payload,
                    )

            wsi = None
            if bioptic_number:
                wsi_payload = self.source_gateway.fetch_wsi(bioptic_number)
                if wsi_payload:
                    wsi = WsiData(
                        bioptic_number=bioptic_number,
                        source_id=str(wsi_payload.get("id", bioptic_number)),
                        payload=wsi_payload,
                    )

            samples.append(
                Sample(
                    sample_id=str(raw_sample["sample_id"]),
                    predictive_number=predictive_number,
                    bioptic_number=bioptic_number,
                    payload=raw_sample,
                    sequencing=sequencing,
                    wsi=wsi,
                )
            )

        accession_numbers = [
            str(value) for value in raw_patient.get("accession_numbers", [])
        ]
        radiology_payloads = self.source_gateway.fetch_radiology(accession_numbers)
        radiology = [
            RadiologyData(
                accession_number=str(item["accession_number"]),
                source_id=str(item.get("id", item["accession_number"])),
                payload=item,
            )
            for item in radiology_payloads
        ]

        return PatientAggregate(
            patient_id=str(raw_patient["patient_id"]),
            accession_numbers=accession_numbers,
            samples=samples,
            payload=raw_patient,
            radiology=radiology,
        )
