import datetime as dt

import xarray as xr
from sqlalchemy.orm import Session

from app.models.domain import Dataset
from app.schemas.domain import MapPreviewIn, TimeSeriesPreviewIn


def _naive_utc(value: dt.datetime) -> dt.datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(dt.timezone.utc).replace(tzinfo=None)


def map_preview(db: Session, payload: MapPreviewIn) -> dict:
    dataset = db.get(Dataset, payload.dataset_id)
    if not dataset or not dataset.storage_path:
        raise ValueError("Dataset storage_path is not configured")
    ds = xr.open_dataset(dataset.storage_path)
    try:
        data = ds["T2"].sel(time=_naive_utc(payload.time), method="nearest")
        return {
            "dataset_id": str(payload.dataset_id),
            "variable_code": payload.variable_code,
            "time": payload.time.isoformat(),
            "tiles": [
                {
                    "lat": float(data["lat"].values[0]),
                    "lon": float(data["lon"].values[0]),
                    "value": float(data.values[0, 0]),
                }
            ],
        }
    finally:
        ds.close()


def time_series_preview(db: Session, payload: TimeSeriesPreviewIn) -> dict:
    dataset = db.get(Dataset, payload.dataset_id)
    if not dataset or not dataset.storage_path:
        raise ValueError("Dataset storage_path is not configured")
    ds = xr.open_dataset(dataset.storage_path)
    try:
        series = (
            ds["T2"]
            .sel(time=slice(_naive_utc(payload.time_start), _naive_utc(payload.time_end)))
            .sel(lat=float(payload.lat), lon=float(payload.lon), method="nearest")
        )
        return {
            "dataset_id": str(payload.dataset_id),
            "variable_code": payload.variable_code,
            "point": {"lat": payload.lat, "lon": payload.lon},
            "series": [
                {"time": str(t), "value": float(v)}
                for t, v in zip(series["time"].values.tolist(), series.values.tolist())
            ],
        }
    finally:
        ds.close()


def legacy_map_preview(payload: MapPreviewIn) -> dict:
    return {
        "dataset_id": str(payload.dataset_id),
        "variable_code": payload.variable_code,
        "time": payload.time.isoformat(),
        "tiles": [{"z": 0, "x": 0, "y": 0, "value": 12.3}],
    }
