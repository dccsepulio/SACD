import hashlib
import json
from pathlib import Path
import pandas as pd


def write_json_result(results_dir: str, file_stem: str, payload: dict) -> tuple[str, int, str]:
    base = Path(results_dir)
    base.mkdir(parents=True, exist_ok=True)
    target = base / f"{file_stem}.json"
    raw = json.dumps(payload).encode("utf-8")
    target.write_bytes(raw)
    checksum = hashlib.sha256(raw).hexdigest()
    return str(target), len(raw), checksum


def write_csv_result(results_dir: str, file_stem: str, frame: pd.DataFrame) -> tuple[str, int, str]:
    base = Path(results_dir)
    base.mkdir(parents=True, exist_ok=True)
    target = base / f"{file_stem}.csv"
    raw = frame.to_csv(index=False).encode("utf-8")
    target.write_bytes(raw)
    checksum = hashlib.sha256(raw).hexdigest()
    return str(target), len(raw), checksum
