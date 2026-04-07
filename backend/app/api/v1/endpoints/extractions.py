import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.domain import ExtractionJob, ExtractionResult
from app.schemas.domain import ExtractionCreate, ExtractionOut, ExtractionResultOut
from app.services.job_service import create_and_run_job

router = APIRouter()


@router.post("", response_model=ExtractionOut, status_code=201)
def create_extraction(payload: ExtractionCreate, db: Session = Depends(get_db)):
    job = create_and_run_job(db, payload)
    return job


@router.get("", response_model=list[ExtractionOut])
def list_jobs(db: Session = Depends(get_db)):
    return db.scalars(select(ExtractionJob).order_by(ExtractionJob.created_at.desc())).all()


@router.get("/{job_id}", response_model=ExtractionOut)
def get_job(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = db.get(ExtractionJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/{job_id}/result", response_model=ExtractionResultOut)
def get_job_result(job_id: uuid.UUID, db: Session = Depends(get_db)):
    result = db.scalar(select(ExtractionResult).where(ExtractionResult.job_id == job_id))
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    return result


@router.get("/{job_id}/download")
def download_result(job_id: uuid.UUID, db: Session = Depends(get_db)):
    result = db.scalar(select(ExtractionResult).where(ExtractionResult.job_id == job_id))
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    path = Path(result.file_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type=result.mime_type, filename=path.name)


@router.delete("/{job_id}", status_code=204)
def delete_job(job_id: uuid.UUID, db: Session = Depends(get_db)):
    job = db.get(ExtractionJob, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    db.delete(job)
    db.commit()
