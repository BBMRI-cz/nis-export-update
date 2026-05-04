from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.models import SyncState, SyncStatus
from infrastructure.db.models import SyncStateORM, SyncStatusDB


def to_domain(orm: SyncStateORM) -> SyncState:
    return SyncState(
        entity_type=orm.entity_type,
        entity_key=orm.entity_key,
        source_fingerprint=orm.source_fingerprint,
        catalogue_remote_id=orm.catalogue_remote_id,
        status=SyncStatus(orm.status.value),
        is_deleted=orm.is_deleted,
        last_seen_at=orm.last_seen_at,
        last_synced_at=orm.last_synced_at,
        last_error=orm.last_error,
        run_id=orm.run_id,
    )


class SyncStateRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, entity_type: str, entity_key: str) -> SyncState | None:
        stmt = (
            select(SyncStateORM)
            .where(SyncStateORM.entity_type == entity_type)
            .where(SyncStateORM.entity_key == entity_key)
            .order_by(SyncStateORM.id.desc())
            .limit(1)
        )
        orm = self.session.execute(stmt).scalar_one_or_none()
        return to_domain(orm) if orm else None

    def save(self, state: SyncState) -> None:
        stmt = (
            select(SyncStateORM)
            .where(SyncStateORM.entity_type == state.entity_type)
            .where(SyncStateORM.entity_key == state.entity_key)
            .order_by(SyncStateORM.id.desc())
            .limit(1)
        )
        existing = self.session.execute(stmt).scalar_one_or_none()
        if existing:
            existing.source_fingerprint = state.source_fingerprint
            existing.catalogue_remote_id = state.catalogue_remote_id
            existing.status = SyncStatusDB(state.status.value)
            existing.is_deleted = state.is_deleted
            existing.last_seen_at = state.last_seen_at
            existing.last_synced_at = state.last_synced_at
            existing.last_error = state.last_error
            existing.run_id = state.run_id
        else:
            self.session.add(
                SyncStateORM(
                    entity_type=state.entity_type,
                    entity_key=state.entity_key,
                    source_fingerprint=state.source_fingerprint,
                    catalogue_remote_id=state.catalogue_remote_id,
                    status=SyncStatusDB(state.status.value),
                    is_deleted=state.is_deleted,
                    last_seen_at=state.last_seen_at,
                    last_synced_at=state.last_synced_at,
                    last_error=state.last_error,
                    run_id=state.run_id,
                )
            )
        self.session.commit()

    def mark_missing_as_deleted(
        self, entity_type: str, seen_keys: set[str], run_id: str
    ) -> list[SyncState]:
        stmt = select(SyncStateORM).where(SyncStateORM.entity_type == entity_type)
        rows = self.session.execute(stmt).scalars().all()
        missing: list[SyncState] = []
        now = datetime.now(timezone.utc)
        for row in rows:
            if row.entity_key in seen_keys or row.is_deleted:
                continue
            row.is_deleted = True
            row.status = SyncStatusDB.DELETED
            row.last_seen_at = now
            row.last_synced_at = now
            row.last_error = None
            row.run_id = run_id
            missing.append(to_domain(row))
        self.session.commit()
        return missing
