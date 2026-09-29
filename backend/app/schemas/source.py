from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import uuid

class NormalizedRecord(BaseModel):
    """Internal standardized representation for collected records across all platforms."""
    platform: str
    external_id: Optional[str] = None
    raw_text: str
    cleaned_text: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    engagement_score: int = 0
    source_url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class SourceMetadataDTO(BaseModel):
    id: Optional[uuid.UUID] = None
    platform: str
    source_url: Optional[str] = None
    query_used: Optional[str] = None
    records_collected: int
    status: str
    error_message: Optional[str] = None
    fetched_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SourceHealthDTO(BaseModel):
    reddit: bool
    youtube: bool
    news: bool
    file_upload: bool
    gemini: bool
    active_sources_count: int
