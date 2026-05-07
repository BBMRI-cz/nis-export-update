from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from domain.models import (
    FixedBlock,
    SlideContainer,
    SlidePreparationAssay,
    WholeSlideImaging,
    WsiData,
)


@dataclass(frozen=True)
class FixedBlockDto:
    block_identifier: str | None = None
    source_material: str | None = None
    name_of_fixative: str | None = None
    embedding_medium: str | None = None
    slide_container: "SlideContainerDto" | None = None


@dataclass(frozen=True)
class SlideContainerDto:
    slide_container_identifier: str | None = None
    source_fixed_block: str | None = None
    container_type: str | None = None
    section_thickness: int | None = None
    cell_type: list[str] | None = None
    tissue_type: list[str] | None = None
    slide_preparation_assay: "SlidePreparationAssayDto" | None = None


@dataclass(frozen=True)
class SlidePreparationAssayDto:
    assay_identifier: str | None = None
    slide_container_identifier: str | None = None
    staining_method: str | None = None
    assay_type: str | None = None
    whole_slide_imaging: "WholeSlideImagingDto" | None = None


@dataclass(frozen=True)
class WholeSlideImagingDto:
    wsi_identifier: str | None = None
    belongs_to_imaging_study: str | None = None
    dicom_images_count: int | None = None
    series_start_date: str | None = None
    body_region: str | None = None
    imaging_device: str | None = None
    manufacturer_of_imaging_device: str | None = None
    software_version: str | None = None
    z_stacking: str | None = None
    objective_lens_magnification: int | None = None
    illumination_method: str | None = None
    illumination_wavelength: int | None = None
    scanning_operation_mode: str | None = None
    tissue_scan_area: int | None = None
    number_of_focal_planes: int | None = None
    distance_between_focal_planes: int | None = None
    pyramid_levels: int | None = None
    colour_icc_profile: str | None = None
    preview_available: bool | None = None
    label_available: bool | None = None
    source_assay: str | None = None
    file_format: str | None = None
    file_size: int | None = None
    image_width: int | None = None
    image_height: int | None = None
    image_depth: int | None = None
    number_of_channels: int | None = None
    channel_resolution: int | None = None
    compression_method: str | None = None
    compression_quality_label: str | None = None
    annotations_available: bool | None = None


def _whole_slide_imaging_to_dto(
    whole_slide_imaging: WholeSlideImaging | None,
) -> WholeSlideImagingDto | None:
    if whole_slide_imaging is None:
        return None
    return WholeSlideImagingDto(**asdict(whole_slide_imaging))


def _slide_preparation_assay_to_dto(
    assay: SlidePreparationAssay | None,
    whole_slide_imaging: WholeSlideImaging | None,
) -> SlidePreparationAssayDto | None:
    if assay is None:
        return None
    return SlidePreparationAssayDto(
        assay_identifier=assay.assay_identifier,
        slide_container_identifier=assay.slide_container_identifier,
        staining_method=assay.staining_method,
        assay_type=assay.assay_type,
        whole_slide_imaging=_whole_slide_imaging_to_dto(whole_slide_imaging),
    )


def _slide_container_to_dto(
    slide_container: SlideContainer | None,
    assay: SlidePreparationAssay | None,
    whole_slide_imaging: WholeSlideImaging | None,
) -> SlideContainerDto | None:
    if slide_container is None:
        return None
    return SlideContainerDto(
        slide_container_identifier=slide_container.slide_container_identifier,
        source_fixed_block=slide_container.source_fixed_block,
        container_type=slide_container.container_type,
        section_thickness=slide_container.section_thickness,
        cell_type=slide_container.cell_type,
        tissue_type=slide_container.tissue_type,
        slide_preparation_assay=_slide_preparation_assay_to_dto(
            assay, whole_slide_imaging
        ),
    )


def _fixed_block_to_dto(
    fixed_block: FixedBlock | None,
    slide_container: SlideContainer | None,
    assay: SlidePreparationAssay | None,
    whole_slide_imaging: WholeSlideImaging | None,
) -> FixedBlockDto | None:
    if fixed_block is None:
        return None
    return FixedBlockDto(
        block_identifier=fixed_block.block_identifier,
        source_material=fixed_block.source_material,
        name_of_fixative=fixed_block.name_of_fixative,
        embedding_medium=fixed_block.embedding_medium,
        slide_container=_slide_container_to_dto(
            slide_container=slide_container,
            assay=assay,
            whole_slide_imaging=whole_slide_imaging,
        ),
    )


def build_wsi_catalogue_dto(wsi: WsiData) -> dict[str, Any]:
    fixed_block_dto = _fixed_block_to_dto(
        fixed_block=wsi.fixed_block,
        slide_container=wsi.slide_container,
        assay=wsi.slide_preparation_assay,
        whole_slide_imaging=wsi.whole_slide_imaging,
    )
    return {
        "bioptic_number": wsi.bioptic_number,
        "source_id": wsi.source_id,
        "fixed_block": asdict(fixed_block_dto) if fixed_block_dto else None,
    }
