import datetime as dt
import uuid
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class DatasetOut(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    source: str | None = None
    temporal_start: dt.datetime | None = None
    temporal_end: dt.datetime | None = None
    spatial_extent: dict | None = None
    resolution_km: float | None = None
    grid_type: str | None = None
    is_active: bool

    model_config = {"from_attributes": True}


class VariableOut(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    code: str
    name: str
    unit: str | None = None
    description: str | None = None
    is_staggered: bool
    dimensions: dict | None = None
    available_levels: list | None = None
    is_derived: bool

    model_config = {"from_attributes": True}


class CoverageOut(BaseModel):
    temporal_start: dt.datetime | None = None
    temporal_end: dt.datetime | None = None
    spatial_extent: dict | None = None
    coverage_geojson: dict | None = None


class ExtractionCreate(BaseModel):
    dataset_id: uuid.UUID
    requested_by: str | None = None
    time_start: dt.datetime
    time_end: dt.datetime
    geometry_type: Literal["point", "bbox"]
    geometry_payload: dict
    variable_selection: list[str] = Field(min_length=1)
    output_format: Literal["csv"] = "csv"
    processing_options: dict = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.time_end < self.time_start:
            raise ValueError("time_end must be greater than or equal to time_start")
        payload_type = str(self.geometry_payload.get("type", "")).lower()
        if payload_type and payload_type != self.geometry_type:
            raise ValueError("geometry_type must match geometry_payload.type")
        return self

    @field_validator("variable_selection")
    @classmethod
    def validate_variables(cls, values: list[str]) -> list[str]:
        cleaned = [v.strip() for v in values if v and v.strip()]
        if not cleaned:
            raise ValueError("variable_selection cannot be empty")
        if len(set(cleaned)) != len(cleaned):
            raise ValueError("variable_selection cannot contain duplicates")
        if cleaned != ["T2"]:
            raise ValueError("This vertical slice only supports variable_selection=['T2']")
        return cleaned

    @field_validator("geometry_payload")
    @classmethod
    def validate_geometry_payload(cls, payload: dict) -> dict:
        if payload.get("type") is None:
            raise ValueError("geometry_payload.type is required")
        if "coordinates" not in payload and "value" not in payload:
            raise ValueError("geometry_payload must include coordinates or value")
        return payload


class ExtractionOut(BaseModel):
    id: uuid.UUID
    dataset_id: uuid.UUID
    status: Literal["pending", "running", "completed", "failed"]
    output_format: str
    created_at: dt.datetime
    error_message: str | None = None

    model_config = {"from_attributes": True}


class ExtractionResultOut(BaseModel):
    job_id: uuid.UUID
    file_path: str
    file_size: int
    checksum: str
    mime_type: str

    model_config = {"from_attributes": True}


class MapPreviewIn(BaseModel):
    dataset_id: uuid.UUID
    variable_code: str
    time: dt.datetime


class TimeSeriesPreviewIn(BaseModel):
    dataset_id: uuid.UUID
    variable_code: str
    lat: float
    lon: float
    time_start: dt.datetime
    time_end: dt.datetime

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.time_end < self.time_start:
            raise ValueError("time_end must be greater than or equal to time_start")
        return self
