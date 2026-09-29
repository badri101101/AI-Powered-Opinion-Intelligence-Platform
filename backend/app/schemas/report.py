from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
import uuid

from app.schemas.ai_specs import KeyFindingSpec, TopicSummarySpec
from app.schemas.metrics import AnalysisMetricsDTO
from app.schemas.source import SourceMetadataDTO

class GeneratedReportDTO(BaseModel):
    id: Optional[uuid.UUID] = None
    report_title: str
    executive_summary: str
    key_findings: List[KeyFindingSpec] = Field(default_factory=list)
    topic_summaries: List[TopicSummarySpec] = Field(default_factory=list)
    trend_narrative: str
    forecast_interpretation: Optional[str] = None
    caveats_and_disclaimers: str
    pdf_file_path: Optional[str] = None
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class FullReportResponse(BaseModel):
    id: uuid.UUID
    original_prompt: str
    category: str
    target_entity: Optional[str] = None
    location_scope: Optional[str] = None
    time_period_days: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    # Nested Report Components
    report: Optional[GeneratedReportDTO] = None
    metrics: Optional[AnalysisMetricsDTO] = None
    sources: List[SourceMetadataDTO] = Field(default_factory=list)
    records_found: int = 0
