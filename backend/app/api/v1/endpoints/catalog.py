import uuid
import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.domain import Dataset, Variable
from app.schemas.domain import CoverageOut, DatasetOut, VariableOut

router = APIRouter()


@router.get("", response_model=list[DatasetOut])
def list_datasets(db: Session = Depends(get_db)):
    return db.scalars(select(Dataset).where(Dataset.is_active.is_(True))).all()


@router.get("/{dataset_id}", response_model=DatasetOut)
def get_dataset(dataset_id: uuid.UUID, db: Session = Depends(get_db)):
    dataset = db.get(Dataset, dataset_id)
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset


@router.get("/{dataset_id}/variables", response_model=list[VariableOut])
def list_variables(dataset_id: uuid.UUID, db: Session = Depends(get_db)):
    return db.scalars(select(Variable).where(Variable.dataset_id == dataset_id)).all()


@router.get("/{dataset_id}/coverage", response_model=CoverageOut)
def get_coverage(dataset_id: uuid.UUID, db: Session = Depends(get_db)):
    row = db.execute(
        select(
            Dataset.temporal_start,
            Dataset.temporal_end,
            Dataset.spatial_extent,
            func.ST_AsGeoJSON(Dataset.coverage_geom),
        ).where(Dataset.id == dataset_id)
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="Dataset not found")
    coverage_geojson = json.loads(row[3]) if row[3] else None
    return CoverageOut(
        temporal_start=row[0],
        temporal_end=row[1],
        spatial_extent=row[2],
        coverage_geojson=coverage_geojson,
    )
