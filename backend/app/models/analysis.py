import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class AnalysisStatus:
    PENDING = "PENDING"
    CLASSIFYING = "CLASSIFYING"
    COLLECTING = "COLLECTING"
    ANALYZING = "ANALYZING"
    GENERATING = "GENERATING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class AnalysisCategory:
    PRODUCT = "PRODUCT"
    POLICY = "POLICY"
    TOPIC = "TOPIC"
    URL = "URL"
    DATASET = "DATASET"

class AnalysisRequest(Base):
    __tablename__ = "analysis_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    original_prompt = Column(Text, nullable=False)
    category = Column(String(50), nullable=True, default=AnalysisCategory.TOPIC)
    target_entity = Column(String(255), nullable=True)
    location_scope = Column(String(255), nullable=True)
    time_period_days = Column(Integer, default=30)
    intent_parameters = Column(JSON, nullable=True, default=dict)
    
    # Execution Tracking
    status = Column(String(50), nullable=False, default=AnalysisStatus.PENDING, index=True)
    current_step = Column(String(255), nullable=False, default="Request received")
    progress_percent = Column(Integer, nullable=False, default=5)
    records_found = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    sources = relationship("SourceMetadata", back_populates="analysis", cascade="all, delete-orphan", lazy="selectin")
    records = relationship("CollectedRecord", back_populates="analysis", cascade="all, delete-orphan", lazy="selectin")
    metrics = relationship("AnalysisMetrics", back_populates="analysis", uselist=False, cascade="all, delete-orphan", lazy="selectin")
    report = relationship("GeneratedReport", back_populates="analysis", uselist=False, cascade="all, delete-orphan", lazy="selectin")
