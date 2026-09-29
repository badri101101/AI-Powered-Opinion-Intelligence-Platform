import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analysis_requests.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    report_title = Column(String(500), nullable=False)
    executive_summary = Column(Text, nullable=False)
    key_findings = Column(JSON, nullable=False, default=list)            # list of {title: str, description: str, impact: str}
    topic_summaries = Column(JSON, nullable=False, default=list)         # list of {topic_name: str, summary: str, sentiment_note: str}
    trend_narrative = Column(Text, nullable=False)
    forecast_interpretation = Column(Text, nullable=True)
    caveats_and_disclaimers = Column(Text, nullable=False)
    
    pdf_file_path = Column(String(1000), nullable=True)
    generated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analysis = relationship("AnalysisRequest", back_populates="report")
