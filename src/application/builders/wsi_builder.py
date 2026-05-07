from __future__ import annotations

from domain.models import (
    FixedBlock,
    SamplePreparation,
    SlideContainer,
    SlidePreparationAssay,
    WholeSlideImaging,
    WsiData,
)


class WsiBuilder:
    def build_wsi(self, bioptic_number: str, payload: dict) -> WsiData:
        fixed_block_payload = payload.get("fixed_block", payload)
        slide_container_payload = payload.get("slide_container", payload)
        assay_payload = payload.get("slide_preparation_assay", payload)
        whole_slide_imaging_payload = payload.get("whole_slide_imaging", payload.get("wsi", payload))

        return WsiData(
            bioptic_number=bioptic_number,
            source_id=str(payload.get("source_id", payload.get("id", bioptic_number))),
            fixed_block=self._build_fixed_block(fixed_block_payload),
            slide_container=self._build_slide_container(slide_container_payload),
            slide_preparation_assay=self._build_slide_preparation_assay(assay_payload),
            whole_slide_imaging=self._build_whole_slide_imaging(whole_slide_imaging_payload),
        )

    def _build_fixed_block(self, payload: object) -> FixedBlock | None:
        if not isinstance(payload, dict) or not payload:
            return None
        sample_preparation_payload = payload.get("sample_preparation")
        if sample_preparation_payload is None and isinstance(payload.get("sample_preparations"), list):
            candidates = [item for item in payload["sample_preparations"] if isinstance(item, dict)]
            sample_preparation_payload = candidates[0] if candidates else None
        return FixedBlock(
            block_identifier=payload.get("block_identifier"),
            source_material=payload.get("source_material"),
            name_of_fixative=payload.get("name_of_fixative"),
            embedding_medium=payload.get("embedding_medium"),
            sample_preparation=self._build_sample_preparation(sample_preparation_payload),
        )

    def _build_sample_preparation(self, payload: object) -> SamplePreparation | None:
        if not isinstance(payload, dict) or not payload:
            return None
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
            sequencing_run=None,
        )

    def _build_slide_container(self, payload: object) -> SlideContainer | None:
        if not isinstance(payload, dict) or not payload:
            return None
        return SlideContainer(
            slide_container_identifier=payload.get("slide_container_identifier"),
            source_fixed_block=payload.get("source_fixed_block"),
            container_type=payload.get("container_type"),
            section_thickness=payload.get("section_thickness"),
            cell_type=payload.get("cell_type"),
            tissue_type=payload.get("tissue_type"),
        )

    def _build_slide_preparation_assay(self, payload: object) -> SlidePreparationAssay | None:
        if not isinstance(payload, dict) or not payload:
            return None
        return SlidePreparationAssay(
            assay_identifier=payload.get("assay_identifier"),
            slide_container_identifier=payload.get("slide_container_identifier"),
            staining_method=payload.get("staining_method"),
            assay_type=payload.get("assay_type"),
        )

    def _build_whole_slide_imaging(self, payload: object) -> WholeSlideImaging | None:
        if not isinstance(payload, dict) or not payload:
            return None
        return WholeSlideImaging(
            wsi_identifier=payload.get("wsi_identifier"),
            belongs_to_imaging_study=payload.get("belongs_to_imaging_study"),
            dicom_images_count=payload.get("dicom_images_count"),
            series_start_date=payload.get("series_start_date"),
            body_region=payload.get("body_region"),
            imaging_device=payload.get("imaging_device"),
            manufacturer_of_imaging_device=payload.get("manufacturer_of_imaging_device"),
            software_version=payload.get("software_version"),
            z_stacking=payload.get("z_stacking"),
            objective_lens_magnification=payload.get("objective_lens_magnification"),
            illumination_method=payload.get("illumination_method"),
            illumination_wavelength=payload.get("illumination_wavelength"),
            scanning_operation_mode=payload.get("scanning_operation_mode"),
            tissue_scan_area=payload.get("tissue_scan_area"),
            number_of_focal_planes=payload.get("number_of_focal_planes"),
            distance_between_focal_planes=payload.get("distance_between_focal_planes"),
            pyramid_levels=payload.get("pyramid_levels"),
            colour_icc_profile=payload.get("colour_icc_profile"),
            preview_available=payload.get("preview_available"),
            label_available=payload.get("label_available"),
            source_assay=payload.get("source_assay"),
            file_format=payload.get("file_format"),
            file_size=payload.get("file_size"),
            image_width=payload.get("image_width"),
            image_height=payload.get("image_height"),
            image_depth=payload.get("image_depth"),
            number_of_channels=payload.get("number_of_channels"),
            channel_resolution=payload.get("channel_resolution"),
            compression_method=payload.get("compression_method"),
            compression_quality_label=payload.get("compression_quality_label"),
            annotations_available=payload.get("annotations_available"),
        )
