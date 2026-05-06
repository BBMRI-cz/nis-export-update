from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
import hashlib
import json


class SyncStatus(Enum):
    PENDING = "pending"
    SYNCED = "synced"
    FAILED = "failed"
    DELETED = "deleted"


class CatalogueOperation(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    SKIP = "skip"


@dataclass(frozen=True)
class SequencingData:
    predictive_number: str
    source_id: str
    payload: dict


@dataclass(frozen=True)
class WsiData:
    bioptic_number: str
    source_id: str
    payload: dict


@dataclass(frozen=True)
class ImagingSeriesBase:
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
class CtSeries(ImagingSeriesBase):
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
class MrSeries(ImagingSeriesBase):
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
class DxSeries(ImagingSeriesBase):
    patient_orientation: str | None = None
    tube_voltage_kvp: int | None = None
    exposure_time_ms: int | None = None
    exposure_mas: int | None = None


@dataclass(frozen=True)
class MgSeries(ImagingSeriesBase):
    tube_voltage_kvp: int | None = None
    exposure_time_ms: int | None = None
    exposure_mas: int | None = None
    compression_force_n: float | None = None


@dataclass(frozen=True)
class UsSeries(ImagingSeriesBase):
    transducer_frequency_mhz: float | None = None
    mechanical_index: float | None = None
    thermal_index: float | None = None


@dataclass(frozen=True)
class WsiSeries(ImagingSeriesBase):
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


@dataclass(frozen=True)
class ImagingStudy:
    accession_number: str
    source_id: str
    imaging_study_identifier: str | None = None
    belongs_to_person: str | None = None
    imaging_modalities: list[str] | None = None
    body_regions: list[str] | None = None
    imaging_procedures: list[str] | None = None
    reason_for_imaging_procedure: list[str] | None = None
    study_start_date: str | None = None
    dicom_series_count: int | None = None
    dicom_images_count: int | None = None
    affiliated_institution: str | None = None
    ct_series: list[CtSeries] | None = None
    mr_series: list[MrSeries] | None = None
    us_series: list[UsSeries] | None = None
    dx_series: list[DxSeries] | None = None
    mg_series: list[MgSeries] | None = None
    wsi_series: list[WsiSeries] | None = None


# Backwards-compatible alias while consumers migrate naming.
RadiologyData = ImagingStudy


@dataclass(frozen=True)
class Sample:
    sample_id: str
    predictive_number: str | None
    bioptic_number: str | None
    payload: dict
    sequencing: SequencingData | None = None
    wsi: WsiData | None = None


@dataclass(frozen=True)
class PatientAggregate:
    patient_id: str
    accession_numbers: list[str]
    samples: list[Sample]
    payload: dict
    radiology: list[ImagingStudy]

    def is_upload_eligible(self) -> bool:
        return len(self.samples) > 0

    def source_fingerprint(self) -> str:
        serialized = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@dataclass
class SyncState:
    entity_type: str
    entity_key: str
    source_fingerprint: str
    catalogue_remote_id: str | None
    status: SyncStatus
    is_deleted: bool
    last_seen_at: datetime
    last_synced_at: datetime | None
    last_error: str | None
    run_id: str


@dataclass(frozen=True)
class PlannedOperation:
    entity_type: str
    entity_key: str
    operation: CatalogueOperation
    payload: dict | None
    source_fingerprint: str | None


def now_utc() -> datetime:
    return datetime.now(timezone.utc)
