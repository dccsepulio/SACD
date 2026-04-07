from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.domain import MapPreviewIn, TimeSeriesPreviewIn
from app.services.preview_service import map_preview, time_series_preview

router = APIRouter()


@router.post("/map-preview")
def create_map_preview(payload: MapPreviewIn, db: Session = Depends(get_db)):
    try:
        return map_preview(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/time-series-preview")
def create_time_series_preview(payload: TimeSeriesPreviewIn, db: Session = Depends(get_db)):
    try:
        return time_series_preview(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
