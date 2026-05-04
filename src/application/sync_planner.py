from domain.models import (
    CatalogueOperation,
    PatientAggregate,
    PlannedOperation,
    SyncState,
)


class FingerprintSyncPlanner:
    def plan_patient(
        self, patient: PatientAggregate, current: SyncState | None
    ) -> PlannedOperation:
        if not patient.is_upload_eligible():
            return PlannedOperation(
                entity_type="patient",
                entity_key=patient.patient_id,
                operation=CatalogueOperation.SKIP,
                payload=None,
                source_fingerprint=None,
            )

        fingerprint = patient.source_fingerprint()
        payload = {"patient": patient}
        if current is None or current.is_deleted:
            return PlannedOperation(
                entity_type="patient",
                entity_key=patient.patient_id,
                operation=CatalogueOperation.CREATE,
                payload=payload,
                source_fingerprint=fingerprint,
            )

        if current.source_fingerprint != fingerprint:
            return PlannedOperation(
                entity_type="patient",
                entity_key=patient.patient_id,
                operation=CatalogueOperation.UPDATE,
                payload=payload,
                source_fingerprint=fingerprint,
            )

        return PlannedOperation(
            entity_type="patient",
            entity_key=patient.patient_id,
            operation=CatalogueOperation.SKIP,
            payload=None,
            source_fingerprint=fingerprint,
        )
