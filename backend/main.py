import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.core.database import init_db
from app.api.router import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("opinion_intel_app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables and ensure storage directory exists
    logger.info("Initializing Opinion Intelligence Platform...")
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)
    try:
        await init_db()
        logger.info("PostgreSQL database tables initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
    yield
    logger.info("Shutting down Opinion Intelligence Platform.")

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Automated AI-Powered Multi-Source Opinion Intelligence Platform",
    lifespan=lifespan
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Router
app.include_router(api_router, prefix="/api/v1")

@app.get("/health", tags=["System Health"])
async def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
