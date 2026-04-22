from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import String, DateTime, Enum, func, JSON
import enum
from datetime import datetime


class Base(DeclarativeBase):
    pass


class PredictiveNumberStatusDB(enum.Enum):
    SOURCE_NOT_FOUND = "source_not_found"
    READY_FOR_UPLOAD = "ready_for_upload"
    UPLOADED = "uploaded"
    UPLOAD_FAILED = "upload_failed"


class PredictiveNumberStateORM(Base):
    __tablename__ = "predictive_number_state"

    pseudo_pred_number: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    real_pred_number: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    status: Mapped[PredictiveNumberStatusDB] = mapped_column(
        Enum(PredictiveNumberStatusDB, native_enum=False),
        nullable=False,
        index=True
    )

    hash: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    runs: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    last_processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    last_error: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )
