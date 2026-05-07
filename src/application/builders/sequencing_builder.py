from __future__ import annotations

from domain.models import (
    Analysis,
    SamplePreparation,
    SequencingEntry,
    SequencingData,
    SequencingRun,
)
from domain.utils import as_list, has_any_keys, resolve_source_id


class SequencingBuilder:
    def build_sequencing_data(
        self, predictive_number: str, payload: dict
    ) -> SequencingData:
        entries_payload = as_list(payload.get("sequencing_entries"))
        if not entries_payload:
            entries_payload = [payload]
        entries: SequencingData = []
        for entry_payload in entries_payload:
            if not isinstance(entry_payload, dict):
                continue
            source_id = resolve_source_id(entry_payload, predictive_number)
            entries.append(
                SequencingEntry(
                    predictive_number=predictive_number,
                    source_id=source_id,
                    fixed_block_identifier=self._build_fixed_block_identifier(
                        entry_payload.get("fixed_block", entry_payload)
                    ),
                    sample_preparation=self._build_sample_preparation(
                        entry_payload.get("sample_preparation", entry_payload)
                    ),
                )
            )
        return entries

    def _build_fixed_block_identifier(self, payload: object) -> str | None:
        if not isinstance(payload, dict) or not payload:
            return None
        return payload.get("block_identifier")

    def _build_sample_preparation(self, payload: object) -> SamplePreparation | None:
        if not isinstance(payload, dict) or not payload:
            return None
        if not has_any_keys(
            payload,
            [
                "sampleprep_identifier",
                "belongs_to_material",
                "input_amount",
                "library_preparation_kit",
                "target_enrichment_kit",
                "sequencing_run",
                "sequencing",
            ],
        ):
            return None
        sequencing_run = None
        direct_run = payload.get("sequencing_run", payload.get("sequencing"))
        if isinstance(direct_run, dict):
            sequencing_run = self._build_sequencing_run(direct_run)
        return SamplePreparation(
            sampleprep_identifier=payload.get("sampleprep_identifier"),
            belongs_to_material=payload.get("belongs_to_material"),
            input_amount=payload.get("input_amount"),
            library_preparation_kit=payload.get("library_preparation_kit"),
            pcr_free=payload.get("pcr_free"),
            target_enrichment_kit=payload.get("target_enrichment_kit"),
            full_sequence_genes=payload.get("full_sequence_genes"),
            partial_sequence_genes=payload.get("partial_sequence_genes"),
            umi=payload.get("umi"),
            intended_insert_size=payload.get("intended_insert_size"),
            intended_read_length=payload.get("intended_read_length"),
            sequencing_run=sequencing_run,
        )

    def _build_sequencing_run(self, payload: object) -> SequencingRun | None:
        if not isinstance(payload, dict) or not payload:
            return None
        if not has_any_keys(
            payload,
            [
                "sequencing_identifier",
                "belongs_to_sample_preparation",
                "sequencing_date",
                "sequencing_platform",
                "instrument_model",
                "sequencing_method",
                "analysis",
            ],
        ):
            return None
        analysis = [
            self._build_analysis(item)
            for item in as_list(payload.get("analysis"))
            if isinstance(item, dict)
        ]
        return SequencingRun(
            sequencing_identifier=payload.get("sequencing_identifier"),
            belongs_to_sample_preparation=payload.get("belongs_to_sample_preparation"),
            sequencing_date=payload.get("sequencing_date"),
            sequencing_platform=payload.get("sequencing_platform"),
            instrument_model=payload.get("instrument_model"),
            sequencing_method=payload.get("sequencing_method"),
            median_read_depth=payload.get("median_read_depth"),
            observed_read_length=payload.get("observed_read_length"),
            observed_insert_size=payload.get("observed_insert_size"),
            percent_q30=payload.get("percent_q30"),
            percent_tr20=payload.get("percent_tr20"),
            sequencing_quality_metrics=payload.get("sequencing_quality_metrics"),
            analysis=analysis[0] if analysis else None,
        )

    def _build_analysis(self, payload: dict) -> Analysis:
        return Analysis(
            analysis_identifier=payload.get("analysis_identifier"),
            belongs_to_sequencing=payload.get("belongs_to_sequencing"),
            physical_location=payload.get("physical_location"),
            abstract_location=payload.get("abstract_location"),
            data_formats=payload.get("data_formats"),
            algorithms=payload.get("algorithms"),
            reference_genome=payload.get("reference_genome"),
            bioinformatic_protocol=payload.get("bioinformatic_protocol"),
            bioinformatic_protocol_deviation=payload.get(
                "bioinformatic_protocol_deviation"
            ),
            reason_for_bioinformatic_protocol_deviation=payload.get(
                "reason_for_bioinformatic_protocol_deviation"
            ),
            wgs_guideline_followed=payload.get("wgs_guideline_followed"),
        )
