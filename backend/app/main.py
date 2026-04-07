import time
from pathlib import Path
import datetime as dt

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, select
from geoalchemy2.elements import WKTElement

from app.api.v1.router import api_router
from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.models.domain import Dataset, Variable
from app.services.subset_service import ensure_example_dataset

app = FastAPI(title=settings.app_name)
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/health")
def root_health() -> dict:
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    for _ in range(30):
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            break
        except Exception:
            time.sleep(1)
    db = SessionLocal()
    try:
        fixture_path = str(Path(settings.results_dir) / "fixtures" / "example_t2.nc")
        fixture_path = ensure_example_dataset(fixture_path)
        exists = db.scalar(select(Dataset.id).limit(1))
        if not exists:
            ds = Dataset(
                name="WRF-Regional-MVP",
                description="Dataset base para MVP",
                source="SACD",
                grid_type="curvilinear",
                temporal_start=dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc),
                temporal_end=dt.datetime(2025, 1, 2, 6, tzinfo=dt.timezone.utc),
                is_active=True,
                spatial_extent={"type": "bbox", "value": [-80.0, -56.0, -66.0, -17.0]},
                storage_path=fixture_path,
                coverage_geom=WKTElement(
                    "MULTIPOLYGON(((-80 -56,-66 -56,-66 -17,-80 -17,-80 -56)))",
                    srid=4326,
                ),
            )
            db.add(ds)
            db.flush()
            db.add_all(
                [
                    Variable(dataset_id=ds.id, code="T2", name="2m Temperature", unit="K"),
                ]
            )
            db.commit()
    finally:
        db.close()
