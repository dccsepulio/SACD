import { useEffect, useState } from "react";
import { apiGet, apiPost } from "./api/client";

type Dataset = { id: string; name: string; description?: string };
type Job = { id: string; status: string; created_at: string };

export function App() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [datasetId, setDatasetId] = useState("");

  async function load() {
    setDatasets(await apiGet<Dataset[]>("/api/v1/datasets"));
    setJobs(await apiGet<Job[]>("/api/v1/extractions"));
  }

  useEffect(() => {
    load().catch(console.error);
  }, []);

  async function createJob() {
    if (!datasetId) return;
    const now = new Date().toISOString();
    await apiPost("/api/v1/extractions", {
      dataset_id: datasetId,
      time_start: now,
      time_end: now,
      geometry_type: "point",
      geometry_payload: { type: "Point", coordinates: [-70, -33] },
      variable_selection: ["T2"],
      output_format: "json",
      processing_options: {},
    });
    await load();
  }

  return (
    <main style={{ fontFamily: "sans-serif", margin: "2rem", maxWidth: 900 }}>
      <h1>SACD Platform MVP</h1>
      <h2>Catalogo</h2>
      <ul>
        {datasets.map((d) => (
          <li key={d.id}>
            <b>{d.name}</b> - {d.description ?? "Sin descripcion"}
          </li>
        ))}
      </ul>

      <h2>Nueva extraccion</h2>
      <select value={datasetId} onChange={(e) => setDatasetId(e.target.value)}>
        <option value="">Selecciona un dataset</option>
        {datasets.map((d) => (
          <option value={d.id} key={d.id}>
            {d.name}
          </option>
        ))}
      </select>
      <button onClick={() => createJob().catch(console.error)} style={{ marginLeft: 12 }}>
        Crear job
      </button>

      <h2>Jobs</h2>
      <ul>
        {jobs.map((j) => (
          <li key={j.id}>
            {j.id} - {j.status} - {new Date(j.created_at).toLocaleString()}
          </li>
        ))}
      </ul>
    </main>
  );
}
