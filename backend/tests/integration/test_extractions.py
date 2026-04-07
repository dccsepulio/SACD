def _base_payload(dataset_id: str) -> dict:
    return {
        "dataset_id": dataset_id,
        "time_start": "2025-01-01T00:00:00Z",
        "time_end": "2025-01-01T18:00:00Z",
        "geometry_type": "point",
        "geometry_payload": {"type": "point", "coordinates": [-70.0, -33.0]},
        "variable_selection": ["T2"],
        "output_format": "csv",
        "processing_options": {},
    }


def test_create_extraction_point_valid(client):
    dataset_id = client.get("/api/v1/datasets").json()[0]["id"]
    payload = _base_payload(dataset_id)
    created = client.post("/api/v1/extractions", json=payload)
    assert created.status_code == 201
    body = created.json()
    assert body["status"] == "completed"

    job_id = body["id"]
    result = client.get(f"/api/v1/extractions/{job_id}/result")
    assert result.status_code == 200
    assert result.json()["job_id"] == job_id
    assert result.json()["mime_type"] == "text/csv"


def test_create_extraction_bbox_valid(client):
    dataset_id = client.get("/api/v1/datasets").json()[0]["id"]
    payload = _base_payload(dataset_id)
    payload["geometry_type"] = "bbox"
    payload["geometry_payload"] = {"type": "bbox", "value": [-70.6, -33.6, -69.9, -32.9]}
    created = client.post("/api/v1/extractions", json=payload)
    assert created.status_code == 201
    assert created.json()["status"] == "completed"


def test_download_result_csv(client):
    dataset_id = client.get("/api/v1/datasets").json()[0]["id"]
    payload = _base_payload(dataset_id)
    created = client.post("/api/v1/extractions", json=payload)
    job_id = created.json()["id"]
    response = client.get(f"/api/v1/extractions/{job_id}/download")
    assert response.status_code == 200
    text = response.text
    assert "time,lat,lon,variable,value" in text
    assert "T2" in text


def test_variable_inexistente_rechazada(client):
    dataset_id = client.get("/api/v1/datasets").json()[0]["id"]
    payload = _base_payload(dataset_id)
    payload["variable_selection"] = ["U10"]
    response = client.post("/api/v1/extractions", json=payload)
    assert response.status_code == 422


def test_rango_temporal_invalido_rechazado(client):
    dataset_id = client.get("/api/v1/datasets").json()[0]["id"]
    payload = _base_payload(dataset_id)
    payload["time_start"] = "2025-01-02T00:00:00Z"
    payload["time_end"] = "2025-01-01T00:00:00Z"
    response = client.post("/api/v1/extractions", json=payload)
    assert response.status_code == 422
