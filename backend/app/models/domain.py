import datetime as dt
import uuid

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geometry

from app.db.session import Base


def utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


class Dataset(Base):
    __tablename__ = "datasets"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text())
    source: Mapped[str | None] = mapped_column(String(120))
    temporal_start: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    temporal_end: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    spatial_extent: Mapped[dict | None] = mapped_column(JSON)
    coverage_geom: Mapped[str | None] = mapped_column(Geometry(geometry_type="MULTIPOLYGON", srid=4326))
    resolution_km: Mapped[float | None] = mapped_column(Float)
    grid_type: Mapped[str | None] = mapped_column(String(50))
    storage_path: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    variables: Mapped[list["Variable"]] = relationship(back_populates="dataset", cascade="all, delete-orphan")


class Variable(Base):
    __tablename__ = "variables"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(80), nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    unit: Mapped[str | None] = mapped_column(String(40))
    description: Mapped[str | None] = mapped_column(Text())
    is_staggered: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    dimensions: Mapped[dict | None] = mapped_column(JSON)
    available_levels: Mapped[list | None] = mapped_column(JSON)
    is_derived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    dataset: Mapped[Dataset] = relationship(back_populates="variables")


class ExtractionJob(Base):
    __tablename__ = "extraction_jobs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("datasets.id"), nullable=False)
    requested_by: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(40), default="pending", nullable=False)
    time_start: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    time_end: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    geometry_type: Mapped[str] = mapped_column(String(40), nullable=False)
    geometry_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    variable_selection: Mapped[list] = mapped_column(JSON, nullable=False)
    output_format: Mapped[str] = mapped_column(String(30), default="netcdf", nullable=False)
    processing_options: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    started_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[str | None] = mapped_column(Text())

    result: Mapped["ExtractionResult | None"] = relationship(back_populates="job", uselist=False)


class ExtractionResult(Base):
    __tablename__ = "extraction_results"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("extraction_jobs.id"), nullable=False, unique=True)
    file_path: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), default="application/netcdf")
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[dt.datetime | None] = mapped_column(DateTime(timezone=True))

    job: Mapped[ExtractionJob] = relationship(back_populates="result")
