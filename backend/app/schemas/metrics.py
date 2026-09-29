from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SentimentDistribution(BaseModel):
    positive: float = Field(..., description="Percentage positive (0-100)")
    neutral: float = Field(..., description="Percentage neutral (0-100)")
    negative: float = Field(..., description="Percentage negative (0-100)")
    average_compound_score: float = Field(..., description="Average compound polarity score (-1.0 to +1.0)")
    label: str = Field(..., description="Overall sentiment descriptor (e.g. Strongly Positive, Moderately Positive, Mixed, etc.)")

class EmotionScores(BaseModel):
    joy: float = Field(0.0, description="Joy / Satisfaction score (0-100)")
    anger: float = Field(0.0, description="Anger / Frustration score (0-100)")
    sadness: float = Field(0.0, description="Sadness / Disappointment score (0-100)")
    trust: float = Field(0.0, description="Trust / Confidence score (0-100)")
    surprise: float = Field(0.0, description="Surprise / Anticipation score (0-100)")

class TopicClusterItem(BaseModel):
    topic_id: int
    name: str = Field(..., description="Auto-generated descriptive cluster label")
    keywords: List[str] = Field(default_factory=list, description="Top keywords in cluster")
    count: int = Field(0, description="Number of items in this cluster")
    share_percentage: float = Field(0.0, description="Percentage of total dataset")
    sentiment_score: float = Field(0.0, description="Average sentiment score for this topic")

class EntityMentionItem(BaseModel):
    entity: str = Field(..., description="Named entity, brand, or feature")
    count: int = Field(0, description="Mention frequency")
    sentiment_score: float = Field(0.0, description="Average associated sentiment")

class TimeSeriesPoint(BaseModel):
    date: str = Field(..., description="ISO Date string YYYY-MM-DD")
    count: int = Field(0, description="Volume count on this date")
    sentiment_score: float = Field(0.0, description="Average sentiment score on this date")

class ProjectedForecastPoint(BaseModel):
    date: str
    projected_sentiment: float
    confidence_lower: float
    confidence_upper: float

class ForecastResult(BaseModel):
    available: bool = Field(False, description="Whether sufficient time-series data exists for forecasting")
    trend_direction: str = Field("STABLE", description="UPWARD, DOWNWARD, STABLE, or INSUFFICIENT_DATA")
    slope: float = Field(0.0, description="Linear regression slope of sentiment momentum")
    confidence: str = Field("LOW", description="HIGH, MEDIUM, LOW, or UNAVAILABLE")
    reason: str = Field("", description="Explanation of calculation or why forecasting was skipped")
    projected_points: List[ProjectedForecastPoint] = Field(default_factory=list)

class AnalysisMetricsDTO(BaseModel):
    total_records_analyzed: int
    sentiment_distribution: SentimentDistribution
    emotion_scores: EmotionScores
    topic_clusters: List[TopicClusterItem]
    entity_mentions: List[EntityMentionItem]
    time_series_trends: List[TimeSeriesPoint]
    forecast_data: ForecastResult
