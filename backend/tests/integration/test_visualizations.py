import datetime as dt


def test_map_preview(client):
    dataset_id = client.get("/api/v1/datasets").json()[0]["id"]
    payload = {
        "dataset_id": dataset_id,
        "variable_code": "T2",
        "time": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
    response = client.post("/api/v1/visualizations/map-preview", json=payload)
    assert response.status_code == 200
    assert "tiles" in response.json()
