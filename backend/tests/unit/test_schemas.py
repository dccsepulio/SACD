import datetime as dt
import uuid

import pytest
from pydantic import ValidationError

from app.schemas.domain import ExtractionCreate


def base_payload():
    now = dt.datetime.now(dt.timezone.utc)
    return {
        "dataset_id": str(uuid.uuid4()),
        "time_start": now.isoformat(),
        "time_end": (now + dt.timedelta(hours=1)).isoformat(),
        "geometry_type": "point",
        "geometry_payload": {"type": "point", "coordinates": [-70.0, -33.0]},
        "variable_selection": ["T2"],
        "output_format": "csv",
        "processing_options": {},
    }


def test_extraction_schema_valid():
    data = ExtractionCreate(**base_payload())
    assert data.output_format == "csv"
    assert data.variable_selection == ["T2"]


def test_extraction_schema_invalid_dates():
    payload = base_payload()
    payload["time_end"] = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=1)).isoformat()
    with pytest.raises(ValidationError):
        ExtractionCreate(**payload)


def test_extraction_schema_invalid_geometry():
    payload = base_payload()
    payload["geometry_payload"] = {"type": "point"}
    with pytest.raises(ValidationError):
        ExtractionCreate(**payload)


def test_extraction_schema_rejects_non_t2():
    payload = base_payload()
    payload["variable_selection"] = ["U10"]
    with pytest.raises(ValidationError):
        ExtractionCreate(**payload)
