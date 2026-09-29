from fastapi import APIRouter
from app.schemas.source import SourceHealthDTO
from app.services.connectors.reddit_conn import reddit_connector
from app.services.connectors.youtube_conn import youtube_connector
from app.services.connectors.news_conn import news_connector
from app.services.connectors.file_conn import file_connector
from app.services.ai.gemini_client import gemini_service

router = APIRouter()

@router.get("/health", response_model=SourceHealthDTO)
async def get_sources_health():
    """Returns connectivity and credential readiness across all external source connectors and Gemini AI."""
    reddit_ok = reddit_connector.is_configured()
    yt_ok = youtube_connector.is_configured()
    news_ok = news_connector.is_configured()
    file_ok = file_connector.is_configured()
    gemini_ok = gemini_service.is_available()

    active_count = sum([reddit_ok, yt_ok, news_ok, file_ok, gemini_ok])

    return SourceHealthDTO(
        reddit=reddit_ok,
        youtube=yt_ok,
        news=news_ok,
        file_upload=file_ok,
        gemini=gemini_ok,
        active_sources_count=active_count
    )
