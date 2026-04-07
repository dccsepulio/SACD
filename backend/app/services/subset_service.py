import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr


def ensure_example_dataset(path: str) -> str:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        return str(target)

    times = pd.date_range("2025-01-01T00:00:00", periods=6, freq="6h")
    lats = np.array([-34.0, -33.5, -33.0, -32.5], dtype=np.float32)
    lons = np.array([-71.0, -70.5, -70.0, -69.5], dtype=np.float32)

    t_idx = np.arange(len(times), dtype=np.float32)[:, None, None]
    lat_idx = np.arange(len(lats), dtype=np.float32)[None, :, None]
    lon_idx = np.arange(len(lons), dtype=np.float32)[None, None, :]
    values = 280.0 + t_idx + (lat_idx * 0.2) + (lon_idx * 0.1)

    ds = xr.Dataset(
        data_vars={"T2": (("time", "lat", "lon"), values)},
        coords={"time": times, "lat": lats, "lon": lons},
        attrs={"title": "SACD extraction fixture"},
    )
    ds["T2"].attrs["units"] = "K"
    ds.to_netcdf(target)
    return str(target)


def _to_naive_utc(value: dt.datetime) -> dt.datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(dt.timezone.utc).replace(tzinfo=None)


def run_subset_to_dataframe(
    dataset_path: str,
    variable_selection: list[str],
    geometry_type: str,
    geometry_payload: dict,
    time_start: dt.datetime,
    time_end: dt.datetime,
) -> pd.DataFrame:
    if variable_selection != ["T2"]:
        raise ValueError("Only variable_selection=['T2'] is supported in this vertical slice")

    ds = xr.open_dataset(dataset_path)
    try:
        if "T2" not in ds.data_vars:
            raise ValueError("Dataset does not contain variable T2")

        t0 = _to_naive_utc(time_start)
        t1 = _to_naive_utc(time_end)
        subset = ds[["T2"]].sel(time=slice(t0, t1))
        if subset.sizes.get("time", 0) == 0:
            raise ValueError("No data found for requested time range")

        if geometry_type == "point":
            lon, lat = geometry_payload["coordinates"]
            subset = subset.sel(lat=float(lat), lon=float(lon), method="nearest")
        elif geometry_type == "bbox":
            min_lon, min_lat, max_lon, max_lat = geometry_payload["value"]
            subset = subset.where(
                (subset["lat"] >= float(min_lat))
                & (subset["lat"] <= float(max_lat))
                & (subset["lon"] >= float(min_lon))
                & (subset["lon"] <= float(max_lon)),
                drop=True,
            )
        else:
            raise ValueError("Only geometry_type point and bbox are supported")

        if geometry_type == "bbox" and (subset.sizes.get("lat", 0) == 0 or subset.sizes.get("lon", 0) == 0):
            raise ValueError("No spatial data found for requested geometry")

        frame = subset["T2"].to_dataframe().reset_index()
        frame = frame.rename(columns={"T2": "value"})
        frame["variable"] = "T2"
        return frame[["time", "lat", "lon", "variable", "value"]]
    finally:
        ds.close()
