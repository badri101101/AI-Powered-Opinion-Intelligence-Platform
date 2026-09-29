from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
import uuid

class AnalysisCreate(BaseModel):
    prompt: str = Field(..., min_length=2, max_length=1000, description="Natural language request or URL")
    category_override: Optional[str] = Field(None, description="Optional manual category override")

class AnalysisStatusResponse(BaseModel):
    id: uuid.UUID
    status: str
    current_step: str
    progress_percent: int
    records_found: int
    error_message: Optional[str] = None
    completed_at: Optional[datetime] = None

class AnalysisListItem(BaseModel):
    id: uuid.UUID
    original_prompt: str
    category: str
    target_entity: Optional[str] = None
    status: str
    records_found: int
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AnalysisListResponse(BaseModel):
    items: List[AnalysisListItem]
    total: int
