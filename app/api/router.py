from fastapi import APIRouter

from app.api.v1.endpoints.healthcheck_router import healthcheck_router
from app.api.v1.endpoints.presigned_router import presigned_router

api_router = APIRouter()

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(healthcheck_router, prefix="/healthcheck", tags=["Healthcheck"])
api_v1_router.include_router(presigned_router, prefix="/presigned", tags=["Presigned"])

api_router.include_router(api_v1_router)
