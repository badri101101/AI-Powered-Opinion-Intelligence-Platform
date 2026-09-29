import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class SourcePlatform:
    REDDIT = "REDDIT"
    YOUTUBE = "YOUTUBE"
    NEWS = "NEWS"
    FILE_UPLOAD = "FILE_UPLOAD"

class SourceMetadata(Base):
    __tablename__ = "source_metadata"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analysis_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    
    platform = Column(String(50), nullable=False)
    source_url = Column(Text, nullable=True)
    query_used = Column(Text, nullable=True)
    records_collected = Column(Integer, default=0, nullable=False)
    status = Column(String(50), default="SUCCESS", nullable=False)
    error_message = Column(Text, nullable=True)
    fetched_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analysis = relationship("AnalysisRequest", back_populates="sources")

class CollectedRecord(Base):
    __tablename__ = "collected_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analysis_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    
    platform = Column(String(50), nullable=False)
    external_id = Column(Text, nullable=True)
    raw_text = Column(Text, nullable=False)
    cleaned_text = Column(Text, nullable=True)
    author = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    engagement_score = Column(Integer, default=0, nullable=False)
    source_url = Column(Text, nullable=True)
    record_metadata = Column(JSON, nullable=True, default=dict)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analysis = relationship("AnalysisRequest", back_populates="records")
