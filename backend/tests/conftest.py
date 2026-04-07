import datetime as dt
import os
import uuid

import pytest
from fastapi.testclient import TestClient
from geoalchemy2.elements import WKTElement
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.db.session import Base, get_db
from app.main import app
from app.models.domain import Dataset, Variable
from app.services.subset_service import ensure_example_dataset


@pytest.fixture()
def client():
    database_url = os.getenv("TEST_DATABASE_URL") or os.getenv("DATABASE_URL") or "sqlite+pysqlite://"
    engine = create_engine(database_url)
    SessionTesting = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    with engine.begin() as conn:
        if database_url.startswith("postgresql"):
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
    if not database_url.startswith("postgresql"):
        Base.metadata.create_all(bind=engine)
    with engine.begin() as conn:
        if database_url.startswith("postgresql"):
            conn.execute(text("TRUNCATE TABLE extraction_results, variables, extraction_jobs, datasets RESTART IDENTITY CASCADE"))
        else:
            conn.execute(text("DELETE FROM extraction_results"))
            conn.execute(text("DELETE FROM variables"))
            conn.execute(text("DELETE FROM extraction_jobs"))
            conn.execute(text("DELETE FROM datasets"))

    db = SessionTesting()
    fixture_path = ensure_example_dataset("/tmp/sacd_test_example_t2.nc")
    ds = Dataset(
        name=f"test-dataset-{uuid.uuid4().hex[:8]}",
        description="dataset for tests",
        source="tests",
        temporal_start=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
        temporal_end=dt.datetime(2025, 1, 2, tzinfo=dt.timezone.utc),
        spatial_extent={"type": "bbox", "value": [-80.0, -56.0, -66.0, -17.0]},
        storage_path=fixture_path,
        coverage_geom=WKTElement(
            "MULTIPOLYGON(((-80 -56,-66 -56,-66 -17,-80 -17,-80 -56)))",
            srid=4326,
        ),
        is_active=True,
    )
    db.add(ds)
    db.flush()
    db.add(Variable(dataset_id=ds.id, code="T2", name="2m temp", unit="K"))
    db.commit()
    db.close()

    def override_get_db():
        session = SessionTesting()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        with engine.begin() as conn:
            if database_url.startswith("postgresql"):
                conn.execute(text("TRUNCATE TABLE extraction_results, variables, extraction_jobs, datasets RESTART IDENTITY CASCADE"))
            else:
                conn.execute(text("DELETE FROM extraction_results"))
                conn.execute(text("DELETE FROM variables"))
                conn.execute(text("DELETE FROM extraction_jobs"))
                conn.execute(text("DELETE FROM datasets"))
