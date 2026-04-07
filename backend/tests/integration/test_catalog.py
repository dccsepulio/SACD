def test_list_datasets(client):
    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(item["name"].startswith("test-dataset-") for item in data)


def test_dataset_coverage(client):
    datasets = client.get("/api/v1/datasets").json()
    dataset_id = datasets[0]["id"]
    response = client.get(f"/api/v1/datasets/{dataset_id}/coverage")
    assert response.status_code == 200
    body = response.json()
    assert body["spatial_extent"]["type"] == "bbox"
    assert body["coverage_geojson"]["type"] == "MultiPolygon"
    assert len(body["coverage_geojson"]["coordinates"]) == 1
