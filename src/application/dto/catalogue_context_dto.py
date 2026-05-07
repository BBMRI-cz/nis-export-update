from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from domain.models import Clinical, Material, PatientAggregate, Personal, Sample


@dataclass(frozen=True)
class PersonalDto:
    personal_identifier: str | None = None
    year_of_birth: int | None = None
    sex_at_birth: str | None = None
    gender_identity: str | None = None


@dataclass(frozen=True)
class ClinicalDto:
    clinical_identifier: str | None = None
    belongs_to_person: str | None = None
    clinical_diagnosis: list[str] | None = None
    age_at_diagnosis: int | None = None
    age_of_onset: int | None = None


@dataclass(frozen=True)
class MaterialDto:
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


def _personal_to_dto(personal: Personal | None) -> PersonalDto | None:
    if personal is None:
        return None
    return PersonalDto(**asdict(personal))


def _clinical_to_dto(clinical: Clinical | None) -> ClinicalDto | None:
    if clinical is None:
        return None
    return ClinicalDto(**asdict(clinical))


def material_to_dto(material: Material | None) -> MaterialDto | None:
    if material is None:
        return None
    return MaterialDto(**asdict(material))


def build_personal_catalogue_dto(patient: PatientAggregate) -> dict[str, Any] | None:
    personal = _personal_to_dto(patient.personal)
    return asdict(personal) if personal else None


def build_clinical_catalogue_dto(patient: PatientAggregate) -> dict[str, Any] | None:
    clinical = _clinical_to_dto(patient.clinical)
    return asdict(clinical) if clinical else None


def build_material_catalogue_dto(sample: Sample) -> dict[str, Any] | None:
    material = material_to_dto(sample.material)
    return asdict(material) if material else None
