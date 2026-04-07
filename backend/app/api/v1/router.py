from fastapi import APIRouter

from app.api.v1.endpoints import catalog, extractions, health, visualizations

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(catalog.router, prefix="/datasets", tags=["catalog"])
api_router.include_router(extractions.router, prefix="/extractions", tags=["extractions"])
api_router.include_router(visualizations.router, prefix="/visualizations", tags=["visualizations"])
