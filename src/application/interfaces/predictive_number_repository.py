from typing import Protocol
from domain.models import PredictiveNumberState


class PredictiveNumberRepository(Protocol):
    def get(self, pseudo_pred_number: str) -> PredictiveNumberState | None:
        ...

    def save(self, state: PredictiveNumberState) -> None:
        ...

    def get_all(self) -> list[PredictiveNumberState]:
        ...
