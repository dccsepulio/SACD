import datetime as dt

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.domain import Dataset, ExtractionJob, ExtractionResult
from app.schemas.domain import ExtractionCreate
from app.services.storage_service import write_csv_result
from app.services.subset_service import run_subset_to_dataframe


def create_and_run_job(db: Session, payload: ExtractionCreate) -> ExtractionJob:
    job = ExtractionJob(
        dataset_id=payload.dataset_id,
        requested_by=payload.requested_by,
        status="pending",
        time_start=payload.time_start,
        time_end=payload.time_end,
        geometry_type=payload.geometry_type,
        geometry_payload=payload.geometry_payload,
        variable_selection=payload.variable_selection,
        output_format="csv",
        processing_options=payload.processing_options,
    )
    db.add(job)
    db.flush()
    db.commit()
    db.refresh(job)

    try:
        dataset = db.get(Dataset, payload.dataset_id)
        if not dataset or not dataset.storage_path:
            raise ValueError("Dataset storage_path is not configured")

        job.status = "running"
        job.started_at = dt.datetime.now(dt.timezone.utc)
        db.commit()
        db.refresh(job)

        frame = run_subset_to_dataframe(
            dataset.storage_path,
            payload.variable_selection,
            payload.geometry_type,
            payload.geometry_payload,
            payload.time_start,
            payload.time_end,
        )
        file_path, file_size, checksum = write_csv_result(
            settings.results_dir,
            str(job.id),
            frame,
        )
        result = ExtractionResult(
            job_id=job.id,
            file_path=file_path,
            file_size=file_size,
            checksum=checksum,
            mime_type="text/csv",
        )
        job.status = "completed"
        job.finished_at = dt.datetime.now(dt.timezone.utc)
        db.add(result)
    except Exception as exc:
        job.status = "failed"
        job.error_message = str(exc)
    db.commit()
    db.refresh(job)
    return job
