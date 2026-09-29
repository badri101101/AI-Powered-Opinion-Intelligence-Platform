from typing import List, Optional, Literal, Dict
from pydantic import BaseModel, Field

class SourceQuerySpec(BaseModel):
    reddit_query: Optional[str] = Field(None, description="Search query keyword for Reddit API")
    reddit_subreddits: Optional[List[str]] = Field(default_factory=list, description="Target subreddit names if applicable")
    youtube_query: Optional[str] = Field(None, description="Search query keyword for YouTube API")
    news_query: Optional[str] = Field(None, description="Search query keyword for News/RSS feeds")

class InputAnalysisSpec(BaseModel):
    """Structured output contract from Gemini AI #1: Input & Workflow Analyzer"""
    category: Literal["PRODUCT", "POLICY", "TOPIC", "URL", "DATASET"] = Field(
        ..., description="Detected category of the analysis request"
    )
    target_entity: str = Field(..., description="Main subject, product name, policy title, or entity")
    secondary_keywords: List[str] = Field(default_factory=list, description="Associated synonyms or aspect keywords")
    location_scope: Optional[str] = Field(None, description="Geographic focus if specified (e.g. India, US, Global)")
    time_period_days: int = Field(30, description="Approximate historical lookback period in days (7, 30, 90, 365)")
    url_target: Optional[str] = Field(None, description="Target direct URL if user provided one")
    recommended_sources: List[Literal["REDDIT", "YOUTUBE", "NEWS", "FILE_UPLOAD"]] = Field(
        default_factory=lambda: ["NEWS", "REDDIT", "YOUTUBE"],
        description="Recommended source connectors for this query"
    )
    source_queries: SourceQuerySpec = Field(default_factory=SourceQuerySpec, description="Optimized queries for each connector")
    confidence_score: float = Field(0.9, ge=0.0, le=1.0, description="Confidence in classification")

class KeyFindingSpec(BaseModel):
    title: str = Field(..., description="Short takeaway heading")
    description: str = Field(..., description="Detailed factual finding supported by numbers")
    impact: Literal["POSITIVE", "NEGATIVE", "NEUTRAL", "MIXED"] = Field("NEUTRAL")

class TopicSummarySpec(BaseModel):
    topic_name: str = Field(..., description="Name of the thematic cluster")
    summary: str = Field(..., description="Factual synthesis of discussions in this topic")
    sentiment_note: str = Field(..., description="Sentiment slant observed in this topic")

class ReportSynthesisSpec(BaseModel):
    """Structured output contract from Gemini AI #2: Report Generator"""
    report_title: str = Field(..., description="Formal executive title of the report")
    executive_summary: str = Field(..., description="High-level narrative summary of opinions and consensus")
    key_findings: List[KeyFindingSpec] = Field(default_factory=list, description="3-5 critical takeaway findings")
    topic_summaries: List[TopicSummarySpec] = Field(default_factory=list, description="Synthesized narrative per topic cluster")
    trend_narrative: str = Field(..., description="Interpretation of sentiment momentum and volume trajectory over time")
    forecast_interpretation: Optional[str] = Field(None, description="Objective interpretation of the statistical forecast, noting limitations")
    caveats_and_disclaimers: str = Field(
        ..., description="Methodology constraints, source limitations, and policy neutrality disclaimer"
    )
