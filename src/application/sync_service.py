from __future__ import annotations

from dataclasses import dataclass
import uuid
from application.builders.clinical_builder import ClinicalBuilder
from application.builders.radiology_builder import RadiologyBuilder
from application.builders.sequencing_builder import SequencingBuilder
from application.builders.wsi_builder import WsiBuilder
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
    SyncState,
    SyncStatus,
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
        clinical_builder: ClinicalBuilder | None = None,
        radiology_builder: RadiologyBuilder | None = None,
        sequencing_builder: SequencingBuilder | None = None,
        wsi_builder: WsiBuilder | None = None,
    ) -> None:
        self.source_gateway = source_gateway
        self.catalogue_gateway = catalogue_gateway
        self.state_repository = state_repository
        self.planner = planner
        self.clinical_builder = clinical_builder or ClinicalBuilder()
        self.radiology_builder = radiology_builder or RadiologyBuilder()
        self.sequencing_builder = sequencing_builder or SequencingBuilder()
        self.wsi_builder = wsi_builder or WsiBuilder()

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
        personal = self.clinical_builder.build_personal(raw_patient)
        clinical = self.clinical_builder.build_clinical(raw_patient)
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
                    sequencing = self.sequencing_builder.build_sequencing_data(
                        predictive_number=predictive_number,
                        payload=sequencing_payload,
                    )

            wsi = None
            if bioptic_number:
                wsi_payload = self.source_gateway.fetch_wsi(bioptic_number)
                if wsi_payload:
                    wsi = self.wsi_builder.build_wsi(
                        bioptic_number=bioptic_number,
                        payload=wsi_payload,
                    )

            samples.append(
                Sample(
                    sample_id=str(raw_sample["sample_id"]),
                    predictive_number=predictive_number,
                    bioptic_number=bioptic_number,
                    material=self.clinical_builder.build_material(raw_sample),
                    payload=raw_sample,
                    sequencing=sequencing,
                    wsi=wsi,
                )
            )

        accession_numbers = [
            str(value) for value in raw_patient.get("accession_numbers", [])
        ]
        radiology_payloads = self.source_gateway.fetch_radiology(accession_numbers)
        radiology: RadiologyData = []
        for item in radiology_payloads:
            if not isinstance(item, dict):
                continue
            radiology.append(self.radiology_builder.build_imaging_study(item))

        return PatientAggregate(
            patient_id=str(raw_patient["patient_id"]),
            accession_numbers=accession_numbers,
            personal=personal,
            clinical=clinical,
            samples=samples,
            payload=raw_patient,
            radiology=radiology,
        )
