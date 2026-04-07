# SACD Climate Platform (MVP)

Monorepo con stack oficial:
- `frontend`: React + Vite
- `backend`: FastAPI + SQLAlchemy + Pydantic
- `db`: PostgreSQL + PostGIS

## Levantar entorno con Docker

1. Copiar variables:
   - `copy .env.example .env` (Windows)
2. Levantar servicios:
   - `docker compose up --build`

Servicios expuestos:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- Healthcheck: `http://localhost:8000/api/v1/health`

## Endpoints MVP backend

- `GET /api/v1/health`
- `GET /api/v1/datasets`
- `GET /api/v1/datasets/{dataset_id}`
- `GET /api/v1/datasets/{dataset_id}/variables`
- `GET /api/v1/datasets/{dataset_id}/coverage`
- `POST /api/v1/extractions`
- `GET /api/v1/extractions`
- `GET /api/v1/extractions/{job_id}`
- `GET /api/v1/extractions/{job_id}/result`
- `GET /api/v1/extractions/{job_id}/download`
- `DELETE /api/v1/extractions/{job_id}`
- `POST /api/v1/visualizations/map-preview`
- `POST /api/v1/visualizations/time-series-preview`

## Notas de migracion

El runtime principal ahora es FastAPI/React. El codigo Django legado se conserva temporalmente como referencia, pero no es el stack oficial para ejecucion del sistema.
