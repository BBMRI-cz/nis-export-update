from sqlalchemy import select
from sqlalchemy.orm import Session

from domain.models import PredictiveNumberState, PredictiveNumberStatus
from infrastructure.db.models import (
    PredictiveNumberStateORM,
    PredictiveNumberStatusDB,
)


def to_domain(orm: PredictiveNumberStateORM) -> PredictiveNumberState:
    return PredictiveNumberState(
        pseudo_pred_number=orm.pseudo_pred_number,
        real_pred_number=orm.real_pred_number,
        status=PredictiveNumberStatus(orm.status.value),
        hash=orm.hash,
        last_seen_at=orm.last_seen_at,
        last_processed_at=orm.last_processed_at,
        last_error=orm.last_error,
    )


def to_orm(domain: PredictiveNumberState) -> PredictiveNumberStateORM:
    return PredictiveNumberStateORM(
        pseudo_pred_number=domain.pseudo_pred_number,
        real_pred_number=domain.real_pred_number,
        status=PredictiveNumberStatusDB(domain.status.value),
        hash=domain.hash,
        last_seen_at=domain.last_seen_at,
        last_processed_at=domain.last_processed_at,
        last_error=domain.last_error,
    )


class PredictiveNumberRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, pseudo_pred_number: str) -> PredictiveNumberState | None:
        orm = self.session.get(PredictiveNumberStateORM, pseudo_pred_number)
        return to_domain(orm) if orm else None

    def get_all(self) -> list[PredictiveNumberState]:
        stmt = select(PredictiveNumberStateORM)
        result = self.session.execute(stmt).scalars().all()
        return [to_domain(row) for row in result]

    def save(self, state: PredictiveNumberState) -> None:
        existing = self.session.get(PredictiveNumberStateORM, state.pseudo_pred_number)

        if existing:
            self._update_existing(existing, state)
        else:
            self.session.add(to_orm(state))

        self.session.commit()

    def _update_existing(
        self, existing: PredictiveNumberStateORM, state: PredictiveNumberState
    ) -> None:
        existing.real_pred_number = state.real_pred_number
        existing.status = PredictiveNumberStatusDB(state.status.value)
        existing.hash = state.hash
        existing.last_seen_at = state.last_seen_at
        existing.last_processed_at = state.last_processed_at
        existing.last_error = state.last_error
