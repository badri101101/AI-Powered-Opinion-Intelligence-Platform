import pytest
import io
import uuid
from app.services.analytics.preprocessor import preprocessor
from app.services.analytics.topics import topic_engine
from app.services.analytics.forecasting import forecasting_engine
from app.services.analytics.sentiment import sentiment_analyzer
from app.services.analytics.emotions import emotion_analyzer
from app.services.ai.input_analyzer import input_analyzer
from app.services.ai.report_writer import report_writer
from app.schemas.source import NormalizedRecord, SourceMetadataDTO
from app.schemas.ai_specs import InputAnalysisSpec
from app.schemas.metrics import AnalysisMetricsDTO, SentimentDistribution, EmotionScores, ForecastResult, TimeSeriesPoint
from datetime import datetime, timezone

@pytest.mark.asyncio
async def test_non_existent_analysis_endpoints(async_client):
    random_id = uuid.uuid4()
    # Status endpoint with non-existent ID
    res_status = await async_client.get(f"/api/v1/analyses/{random_id}/status")
    assert res_status.status_code == 404

    # Report endpoint with non-existent ID
    res_report = await async_client.get(f"/api/v1/analyses/{random_id}/report")
    assert res_report.status_code == 404

    # PDF endpoint with non-existent ID
    res_pdf = await async_client.get(f"/api/v1/analyses/{random_id}/export/pdf")
    assert res_pdf.status_code == 404

@pytest.mark.asyncio
async def test_upload_invalid_file_extensions(async_client):
    # Test uploading .txt file
    file_payload = {"file": ("test.txt", b"Some random text data", "text/plain")}
    res = await async_client.post("/api/v1/analyses/upload", files=file_payload)
    assert res.status_code == 400
    assert "Only CSV (.csv) and Excel (.xlsx, .xls) files are supported" in res.json()["detail"]

    # Test uploading empty .csv file
    empty_payload = {"file": ("empty.csv", b"", "text/csv")}
    res_empty = await async_client.post("/api/v1/analyses/upload", files=empty_payload)
    assert res_empty.status_code == 400
    assert "Uploaded file is empty" in res_empty.json()["detail"]

def test_data_preprocessor_robustness():
    dirty_text = "Check out https://t.co/xyz123 &amp; &lt;b&gt;Samsung S26&lt;/b&gt;!! #Awesome 👍👍"
    cleaned = preprocessor.clean_text(dirty_text)
    assert "https://" not in cleaned
    assert "<b>" not in cleaned
    assert "&amp;" not in cleaned
    assert "Samsung S26" in cleaned

    # Test deduplication
    records = [
        NormalizedRecord(platform="NEWS", raw_text="Identical duplicate content text."),
        NormalizedRecord(platform="NEWS", raw_text="Identical duplicate content text."),
        NormalizedRecord(platform="NEWS", raw_text="   "), # Empty text
        NormalizedRecord(platform="NEWS", raw_text="Unique second content text.")
    ]
    processed = preprocessor.preprocess_records(records)
    assert len(processed) == 2
    assert processed[0].raw_text != processed[1].raw_text

def test_sparse_data_topic_and_forecast():
    # Sparse records (e.g. only 1 record)
    single_record = [
        NormalizedRecord(platform="NEWS", raw_text="Great device with fast performance.", cleaned_text="great device fast performance")
    ]
    clusters = topic_engine.extract_topics(single_record, sentiment_scores=[0.8], num_topics=3)
    assert isinstance(clusters, list)
    assert len(clusters) >= 1

    # Single date time-series (insufficient for linear regression)
    time_points = [
        TimeSeriesPoint(date="2026-03-01", count=1, sentiment_score=0.5)
    ]
    forecast = forecasting_engine.forecast(time_points)
    assert forecast.available is False
    assert forecast.trend_direction == "INSUFFICIENT_DATA"
    assert "Insufficient historical time-series data points" in forecast.reason

def test_gemini_fallback_compilers():
    # Test input analyzer heuristic compiler
    fallback_intent = input_analyzer._heuristic_fallback("Analyze public discussion about the new EV policy in India", "POLICY")
    assert fallback_intent.category == "POLICY"
    assert "EV policy" in fallback_intent.target_entity or "policy in India" in fallback_intent.target_entity
    assert "NEWS" in fallback_intent.recommended_sources

    # Test report writer compiler
    metrics = AnalysisMetricsDTO(
        total_records_analyzed=10,
        sentiment_distribution=SentimentDistribution(
            positive=70.0,
            neutral=20.0,
            negative=10.0,
            average_compound_score=0.45,
            label="Moderately Positive"
        ),
        emotion_scores=EmotionScores(joy=40.0, trust=30.0, surprise=10.0, sadness=5.0, anger=5.0),
        topic_clusters=[],
        entity_mentions=[],
        time_series_trends=[],
        forecast_data=ForecastResult(available=False, trend_direction="INSUFFICIENT_DATA", slope=0.0, confidence="LOW", reason="Sparse data")
    )
    sources = [
        SourceMetadataDTO(
            platform="NEWS",
            source_url="https://news.google.com",
            query_used="EV policy",
            records_collected=10,
            status="SUCCESS",
            fetched_at=datetime.now(timezone.utc)
        )
    ]
    report = report_writer._deterministic_compiler(
        "Analyze EV policy in India",
        fallback_intent,
        metrics,
        sources
    )
    assert report.report_title.startswith("Multi-Source Opinion Intelligence Brief")
    assert "moderately positive" in report.executive_summary.lower()
    assert len(report.key_findings) >= 2
    assert "Methodology" in report.caveats_and_disclaimers
