from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from domain.models import (
    Analysis,
    SamplePreparation,
    SequencingEntry,
    SequencingData,
    SequencingRun,
)


@dataclass(frozen=True)
class SamplePreparationDto:
    sampleprep_identifier: str | None = None
    belongs_to_material: str | None = None
    input_amount: str | None = None
    library_preparation_kit: str | None = None
    pcr_free: bool | None = None
    target_enrichment_kit: str | None = None
    full_sequence_genes: list[str] | None = None
    partial_sequence_genes: list[str] | None = None
    umi: bool | None = None
    intended_insert_size: int | None = None
    intended_read_length: int | None = None
    sequencing_run: "SequencingRunDto" | None = None


@dataclass(frozen=True)
class FixedBlockDto:
    block_identifier: str | None = None
    sample_preparation: SamplePreparationDto | None = None


@dataclass(frozen=True)
class SequencingRunDto:
    sequencing_identifier: str | None = None
    belongs_to_sample_preparation: str | None = None
    sequencing_date: str | None = None
    sequencing_platform: str | None = None
    instrument_model: str | None = None
    sequencing_method: str | None = None
    median_read_depth: int | None = None
    observed_read_length: int | None = None
    observed_insert_size: int | None = None
    percent_q30: float | None = None
    percent_tr20: float | None = None
    sequencing_quality_metrics: str | None = None
    analysis: "AnalysisDto" | None = None


@dataclass(frozen=True)
class AnalysisDto:
    analysis_identifier: str | None = None
    belongs_to_sequencing: str | None = None
    physical_location: str | None = None
    abstract_location: str | None = None
    data_formats: list[str] | None = None
    algorithms: list[str] | None = None
    reference_genome: str | None = None
    bioinformatic_protocol: str | None = None
    bioinformatic_protocol_deviation: str | None = None
    reason_for_bioinformatic_protocol_deviation: str | None = None
    wgs_guideline_followed: str | None = None


@dataclass(frozen=True)
class SequencingEntryDto:
    predictive_number: str
    source_id: str
    fixed_block: FixedBlockDto | None = None


def _sample_preparation_to_dto(
    sample_preparation: SamplePreparation | None,
) -> SamplePreparationDto | None:
    if sample_preparation is None:
        return None
    return SamplePreparationDto(
        sampleprep_identifier=sample_preparation.sampleprep_identifier,
        belongs_to_material=sample_preparation.belongs_to_material,
        input_amount=sample_preparation.input_amount,
        library_preparation_kit=sample_preparation.library_preparation_kit,
        pcr_free=sample_preparation.pcr_free,
        target_enrichment_kit=sample_preparation.target_enrichment_kit,
        full_sequence_genes=sample_preparation.full_sequence_genes,
        partial_sequence_genes=sample_preparation.partial_sequence_genes,
        umi=sample_preparation.umi,
        intended_insert_size=sample_preparation.intended_insert_size,
        intended_read_length=sample_preparation.intended_read_length,
        sequencing_run=_sequencing_run_to_dto(sample_preparation.sequencing_run)
        if sample_preparation.sequencing_run
        else None,
    )


def _sequencing_run_to_dto(
    sequencing_run: SequencingRun | None,
) -> SequencingRunDto | None:
    if sequencing_run is None:
        return None
    return SequencingRunDto(
        sequencing_identifier=sequencing_run.sequencing_identifier,
        belongs_to_sample_preparation=sequencing_run.belongs_to_sample_preparation,
        sequencing_date=sequencing_run.sequencing_date,
        sequencing_platform=sequencing_run.sequencing_platform,
        instrument_model=sequencing_run.instrument_model,
        sequencing_method=sequencing_run.sequencing_method,
        median_read_depth=sequencing_run.median_read_depth,
        observed_read_length=sequencing_run.observed_read_length,
        observed_insert_size=sequencing_run.observed_insert_size,
        percent_q30=sequencing_run.percent_q30,
        percent_tr20=sequencing_run.percent_tr20,
        sequencing_quality_metrics=sequencing_run.sequencing_quality_metrics,
        analysis=_analysis_to_dto(sequencing_run.analysis)
        if sequencing_run.analysis
        else None,
    )


def _analysis_to_dto(analysis: Analysis) -> AnalysisDto:
    return AnalysisDto(**asdict(analysis))


def _fixed_block_to_dto(sequencing: SequencingEntry) -> FixedBlockDto | None:
    if not sequencing.fixed_block_identifier and sequencing.sample_preparation is None:
        return None
    return FixedBlockDto(
        block_identifier=sequencing.fixed_block_identifier,
        sample_preparation=_sample_preparation_to_dto(sequencing.sample_preparation),
    )


def sequencing_entry_to_dto(sequencing: SequencingEntry) -> SequencingEntryDto:
    return SequencingEntryDto(
        predictive_number=sequencing.predictive_number,
        source_id=sequencing.source_id,
        fixed_block=_fixed_block_to_dto(sequencing),
    )


def build_sequencing_catalogue_dto(sequencing: SequencingData) -> list[dict[str, Any]]:
    return [asdict(sequencing_entry_to_dto(item)) for item in sequencing]
