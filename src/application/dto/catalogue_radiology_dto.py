from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from domain.models import (
    CtSeries,
    DxSeries,
    ImagingSeriesBase,
    ImagingStudy,
    MgSeries,
    MrSeries,
    UsSeries,
)


@dataclass(frozen=True)
class ImagingStudyDto:
    accession_number: str
    source_id: str
    imaging_study_identifier: str | None
    belongs_to_person: str | None
    imaging_modalities: list[str] | None
    body_regions: list[str] | None
    imaging_procedures: list[str] | None
    reason_for_imaging_procedure: list[str] | None
    study_start_date: str | None
    dicom_series_count: int | None
    dicom_images_count: int | None
    affiliated_institution: str | None
    ct_series: "CtSeriesDto" | None
    mr_series: "MrSeriesDto" | None
    us_series: "UsSeriesDto" | None
    dx_series: "DxSeriesDto" | None
    mg_series: "MgSeriesDto" | None


@dataclass(frozen=True)
class ImagingSeriesBaseDto:
    source_id: str
    series_identifier: str | None
    imaging_study_identifier: str | None
    dicom_images_count: int | None = None
    series_start_date: str | None = None
    body_region: str | None = None
    laterality: str | None = None
    imaging_device: str | None = None
    manufacturer_of_imaging_device: str | None = None
    software_version: str | None = None
    color_space: str | None = None
    pixel_spacing: int | None = None
    image_type: str | None = None
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


@dataclass(frozen=True)
class CtSeriesDto(ImagingSeriesBaseDto):
    tube_voltage_kvp: int | None = None
    x_ray_tube_current_ma: int | None = None
    exposure_time_ms: int | None = None
    spiral_pitch_factor: float | None = None
    filter_type: str | None = None
    convolution_kernel: str | None = None
    field_of_view: float | None = None
    slice_thickness: float | None = None
    imaging_injection: str | None = None
    number_of_image_planes: int | None = None


@dataclass(frozen=True)
class MrSeriesDto(ImagingSeriesBaseDto):
    sequence_name: str | None = None
    magnetic_field_strength: float | None = None
    mr_acquisition_type: str | None = None
    repetition_time: float | None = None
    echo_time: float | None = None
    imaging_frequency: float | None = None
    flip_angle: int | None = None
    inversion_time: int | None = None
    receive_coil_name: str | None = None
    field_of_view: float | None = None
    slice_thickness: float | None = None
    imaging_injection: str | None = None
    number_of_image_planes: int | None = None


@dataclass(frozen=True)
class UsSeriesDto(ImagingSeriesBaseDto):
    transducer_frequency_mhz: float | None = None
    mechanical_index: float | None = None
    thermal_index: float | None = None


@dataclass(frozen=True)
class DxSeriesDto(ImagingSeriesBaseDto):
    patient_orientation: str | None = None
    tube_voltage_kvp: int | None = None
    exposure_time_ms: int | None = None
    exposure_mas: int | None = None


@dataclass(frozen=True)
class MgSeriesDto(ImagingSeriesBaseDto):
    tube_voltage_kvp: int | None = None
    exposure_time_ms: int | None = None
    exposure_mas: int | None = None
    compression_force_n: float | None = None


def _base_series_kwargs(series: ImagingSeriesBase) -> dict[str, Any]:
    return {
        "source_id": series.source_id,
        "series_identifier": series.series_identifier,
        "imaging_study_identifier": series.imaging_study_identifier,
        "dicom_images_count": series.dicom_images_count,
        "series_start_date": series.series_start_date,
        "body_region": series.body_region,
        "laterality": series.laterality,
        "imaging_device": series.imaging_device,
        "manufacturer_of_imaging_device": series.manufacturer_of_imaging_device,
        "software_version": series.software_version,
        "color_space": series.color_space,
        "pixel_spacing": series.pixel_spacing,
        "image_type": series.image_type,
        "file_format": series.file_format,
        "file_size": series.file_size,
        "image_width": series.image_width,
        "image_height": series.image_height,
        "image_depth": series.image_depth,
        "number_of_channels": series.number_of_channels,
        "channel_resolution": series.channel_resolution,
        "compression_method": series.compression_method,
        "compression_quality_label": series.compression_quality_label,
        "annotations_available": series.annotations_available,
    }


def imaging_study_to_dto(study: ImagingStudy) -> ImagingStudyDto:
    return ImagingStudyDto(
        accession_number=study.accession_number,
        source_id=study.source_id,
        imaging_study_identifier=study.imaging_study_identifier,
        belongs_to_person=study.belongs_to_person,
        imaging_modalities=study.imaging_modalities,
        body_regions=study.body_regions,
        imaging_procedures=study.imaging_procedures,
        reason_for_imaging_procedure=study.reason_for_imaging_procedure,
        study_start_date=study.study_start_date,
        dicom_series_count=study.dicom_series_count,
        dicom_images_count=study.dicom_images_count,
        affiliated_institution=study.affiliated_institution,
        ct_series=ct_series_to_dto(study.ct_series) if study.ct_series else None,
        mr_series=mr_series_to_dto(study.mr_series) if study.mr_series else None,
        us_series=us_series_to_dto(study.us_series) if study.us_series else None,
        dx_series=dx_series_to_dto(study.dx_series) if study.dx_series else None,
        mg_series=mg_series_to_dto(study.mg_series) if study.mg_series else None,
    )


def ct_series_to_dto(series: CtSeries) -> CtSeriesDto:
    return CtSeriesDto(
        **_base_series_kwargs(series),
        tube_voltage_kvp=series.tube_voltage_kvp,
        x_ray_tube_current_ma=series.x_ray_tube_current_ma,
        exposure_time_ms=series.exposure_time_ms,
        spiral_pitch_factor=series.spiral_pitch_factor,
        filter_type=series.filter_type,
        convolution_kernel=series.convolution_kernel,
        field_of_view=series.field_of_view,
        slice_thickness=series.slice_thickness,
        imaging_injection=series.imaging_injection,
        number_of_image_planes=series.number_of_image_planes,
    )


def mr_series_to_dto(series: MrSeries) -> MrSeriesDto:
    return MrSeriesDto(
        **_base_series_kwargs(series),
        sequence_name=series.sequence_name,
        magnetic_field_strength=series.magnetic_field_strength,
        mr_acquisition_type=series.mr_acquisition_type,
        repetition_time=series.repetition_time,
        echo_time=series.echo_time,
        imaging_frequency=series.imaging_frequency,
        flip_angle=series.flip_angle,
        inversion_time=series.inversion_time,
        receive_coil_name=series.receive_coil_name,
        field_of_view=series.field_of_view,
        slice_thickness=series.slice_thickness,
        imaging_injection=series.imaging_injection,
        number_of_image_planes=series.number_of_image_planes,
    )


def us_series_to_dto(series: UsSeries) -> UsSeriesDto:
    return UsSeriesDto(
        **_base_series_kwargs(series),
        transducer_frequency_mhz=series.transducer_frequency_mhz,
        mechanical_index=series.mechanical_index,
        thermal_index=series.thermal_index,
    )


def dx_series_to_dto(series: DxSeries) -> DxSeriesDto:
    return DxSeriesDto(
        **_base_series_kwargs(series),
        patient_orientation=series.patient_orientation,
        tube_voltage_kvp=series.tube_voltage_kvp,
        exposure_time_ms=series.exposure_time_ms,
        exposure_mas=series.exposure_mas,
    )


def mg_series_to_dto(series: MgSeries) -> MgSeriesDto:
    return MgSeriesDto(
        **_base_series_kwargs(series),
        tube_voltage_kvp=series.tube_voltage_kvp,
        exposure_time_ms=series.exposure_time_ms,
        exposure_mas=series.exposure_mas,
        compression_force_n=series.compression_force_n,
    )


def build_radiology_catalogue_dto(study: ImagingStudy) -> dict[str, Any]:
    return {
        "imaging_study": asdict(imaging_study_to_dto(study)),
    }
