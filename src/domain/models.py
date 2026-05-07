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
class Analysis:
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
class Material:
    material_identifier: str | None = None
    collected_from_person: str | None = None
    belongs_to_diagnosis: list[str] | None = None
    sampling_timestamp: str | None = None
    registration_timestamp: str | None = None
    sampling_protocol: str | None = None
    sampling_protocol_deviation: str | None = None
    reason_for_sampling_protocol_deviation: str | None = None
    biospecimen_type: str | None = None
    anatomical_source: str | None = None
    pathological_state: str | None = None
    storage_conditions: str | None = None
    expiration_date: str | None = None
    percentage_tumor_cells: float | None = None
    physical_location: str | None = None
    analyses_performed: list[str] | None = None
    derived_from: str | None = None


@dataclass(frozen=True)
class FixedBlock:
    block_identifier: str | None = None
    source_material: str | None = None
    name_of_fixative: str | None = None
    embedding_medium: str | None = None
    sample_preparation: "SamplePreparation" | None = None
    slide_container: "SlideContainer" | None = None


@dataclass(frozen=True)
class SamplePreparation:
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
    sequencing_run: "SequencingRun" | None = None


@dataclass(frozen=True)
class SequencingRun:
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
    analysis: Analysis | None = None


@dataclass(frozen=True)
class SequencingEntry:
    predictive_number: str
    source_id: str
    fixed_block_identifier: str | None = None
    sample_preparation: SamplePreparation | None = None


SequencingData = list[SequencingEntry]


@dataclass(frozen=True)
class Personal:
    personal_identifier: str | None = None
    year_of_birth: int | None = None
    sex_at_birth: str | None = None
    gender_identity: str | None = None


@dataclass(frozen=True)
class Clinical:
    clinical_identifier: str | None = None
    belongs_to_person: str | None = None
    clinical_diagnosis: list[str] | None = None
    age_at_diagnosis: int | None = None
    age_of_onset: int | None = None


@dataclass(frozen=True)
class SlideContainer:
    slide_container_identifier: str | None = None
    source_fixed_block: str | None = None
    container_type: str | None = None
    section_thickness: int | None = None
    cell_type: list[str] | None = None
    tissue_type: list[str] | None = None
    slide_preparation_assay: "SlidePreparationAssay" | None = None


@dataclass(frozen=True)
class SlidePreparationAssay:
    assay_identifier: str | None = None
    slide_container_identifier: str | None = None
    staining_method: str | None = None
    assay_type: str | None = None
    whole_slide_imaging: "WholeSlideImaging" | None = None


@dataclass(frozen=True)
class WholeSlideImaging:
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


@dataclass(frozen=True)
class WsiData:
    bioptic_number: str
    source_id: str
    fixed_block: FixedBlock | None = None


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
    ct_series: CtSeries | None = None
    mr_series: MrSeries | None = None
    us_series: UsSeries | None = None
    dx_series: DxSeries | None = None
    mg_series: MgSeries | None = None


RadiologyData = list[ImagingStudy]


@dataclass(frozen=True)
class Sample:
    sample_id: str
    predictive_number: str | None
    bioptic_number: str | None
    payload: dict
    material: Material | None = None
    sequencing: SequencingData | None = None
    wsi: WsiData | None = None


@dataclass(frozen=True)
class PatientAggregate:
    patient_id: str
    accession_numbers: list[str]
    personal: Personal | None
    clinical: Clinical | None
    samples: list[Sample]
    payload: dict
    radiology: RadiologyData

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
