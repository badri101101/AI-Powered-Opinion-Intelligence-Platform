import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base

class AnalysisMetrics(Base):
    __tablename__ = "analysis_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analysis_requests.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    
    total_records_analyzed = Column(Integer, default=0, nullable=False)
    
    # Quantitative Statistical Payloads
    sentiment_distribution = Column(JSON, nullable=False, default=dict)  # {pos: float, neu: float, neg: float, avg_score: float, label: str}
    emotion_scores = Column(JSON, nullable=False, default=dict)          # {joy: float, anger: float, sadness: float, trust: float, surprise: float}
    topic_clusters = Column(JSON, nullable=False, default=list)          # list of {topic_id, name, keywords, count, sentiment_score, share}
    entity_mentions = Column(JSON, nullable=False, default=list)         # list of {entity: str, count: int, sentiment: float}
    time_series_trends = Column(JSON, nullable=False, default=list)      # list of {date: str, count: int, sentiment_score: float}
    forecast_data = Column(JSON, nullable=False, default=dict)           # {available: bool, trend_direction: str, slope: float, confidence: str, reason: str, projected_points: list}
    
    computed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    analysis = relationship("AnalysisRequest", back_populates="metrics")
