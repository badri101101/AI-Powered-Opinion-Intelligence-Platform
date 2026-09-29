import pytest
from datetime import datetime, timezone, timedelta
from app.schemas.source import NormalizedRecord
from app.services.analytics.engine import analytics_engine

def test_analytics_pipeline_execution():
    now = datetime.now(timezone.utc)
    sample_records = [
        NormalizedRecord(
            platform="NEWS",
            raw_text="The battery life on this new smartphone is incredible and lasts over two days. Love it!",
            published_at=now - timedelta(days=2)
        ),
        NormalizedRecord(
            platform="NEWS",
            raw_text="Amazing camera quality and top tier performance. Highly recommended!",
            published_at=now - timedelta(days=1)
        ),
        NormalizedRecord(
            platform="NEWS",
            raw_text="Terrible pricing and awful customer support. Very disappointed with the build.",
            published_at=now
        ),
        NormalizedRecord(
            platform="NEWS",
            raw_text="Government subsidy policy offers solid tax incentives for clean energy buyers.",
            published_at=now
        )
    ]

    metrics = analytics_engine.analyze(sample_records)
    
    assert metrics.total_records_analyzed == 4
    assert metrics.sentiment_distribution.positive > 0
    assert metrics.sentiment_distribution.negative > 0
    assert len(metrics.topic_clusters) > 0
    assert len(metrics.time_series_trends) >= 2
    assert metrics.forecast_data is not None
