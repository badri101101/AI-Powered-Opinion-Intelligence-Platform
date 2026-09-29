from fastapi import APIRouter
from app.api.v1.analyses import router as analyses_router
from app.api.v1.reports import router as reports_router
from app.api.v1.sources import router as sources_router

api_router = APIRouter()

api_router.include_router(analyses_router, prefix="/analyses", tags=["Analyses"])
api_router.include_router(reports_router, prefix="/analyses", tags=["Reports & Export"])
api_router.include_router(sources_router, prefix="/sources", tags=["Sources Health"])
