import os
import uuid
import pytest
from datetime import datetime, timezone
from app.schemas.report import FullReportResponse, GeneratedReportDTO
from app.schemas.metrics import AnalysisMetricsDTO, SentimentDistribution, EmotionScores, TopicClusterItem, ForecastResult
from app.schemas.source import SourceMetadataDTO
from app.services.export.pdf_builder import pdf_builder

def test_pdf_generation():
    test_id = uuid.uuid4()
    report_dto = GeneratedReportDTO(
        report_title="Test Opinion Intelligence Report",
        executive_summary="This is an automated test summary verifying PDF compilation.",
        key_findings=[],
        topic_summaries=[],
        trend_narrative="Positive trend momentum observed across news cycles.",
        forecast_interpretation="Stable forecast.",
        caveats_and_disclaimers="For testing purposes only.",
        generated_at=datetime.now(timezone.utc)
    )

    metrics_dto = AnalysisMetricsDTO(
        total_records_analyzed=10,
        sentiment_distribution=SentimentDistribution(
            positive=60.0,
            neutral=30.0,
            negative=10.0,
            average_compound_score=0.45,
            label="Moderately Positive"
        ),
        emotion_scores=EmotionScores(joy=40.0, trust=30.0, anger=10.0, sadness=10.0, surprise=10.0),
        topic_clusters=[TopicClusterItem(topic_id=1, name="Battery & Camera", keywords=["battery", "camera"], count=10, share_percentage=100.0, sentiment_score=0.5)],
        entity_mentions=[],
        time_series_trends=[],
        forecast_data=ForecastResult(available=False, trend_direction="STABLE", slope=0.0, confidence="LOW", reason="Test reason", projected_points=[])
    )

    full_report = FullReportResponse(
        id=test_id,
        original_prompt="Analyze Samsung Galaxy S26 reviews",
        category="PRODUCT",
        target_entity="Samsung Galaxy S26",
        location_scope="Global",
        time_period_days=30,
        status="COMPLETED",
        created_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        report=report_dto,
        metrics=metrics_dto,
        sources=[SourceMetadataDTO(platform="NEWS", source_url="https://news.google.com", records_collected=10, status="SUCCESS", fetched_at=datetime.now(timezone.utc))],
        records_found=10
    )

    pdf_path = pdf_builder.generate_pdf(full_report)
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 1000
