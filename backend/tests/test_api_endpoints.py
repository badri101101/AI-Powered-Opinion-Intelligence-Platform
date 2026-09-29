import pytest
import uuid
from app.services.orchestrator import orchestrator
from app.core.database import AsyncSessionLocal
from app.models.analysis import AnalysisRequest, AnalysisStatus
from app.schemas.source import NormalizedRecord

@pytest.mark.asyncio
async def test_health_endpoint(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_sources_health_endpoint(async_client):
    response = await async_client.get("/api/v1/sources/health")
    assert response.status_code == 200
    data = response.json()
    assert "news" in data
    assert data["news"] is True
    assert "active_sources_count" in data

@pytest.mark.asyncio
async def test_create_analysis_empty_validation(async_client):
    # Empty prompt validation test
    response = await async_client.post("/api/v1/analyses", json={"prompt": "   "})
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_end_to_end_orchestrator_pipeline():
    # Directly test complete orchestrator execution on sample dataset
    async with AsyncSessionLocal() as db:
        analysis = AnalysisRequest(
            original_prompt="Analyze Samsung Galaxy S26 battery and camera reviews",
            category="PRODUCT",
            target_entity="Samsung Galaxy S26",
            status=AnalysisStatus.PENDING,
            current_step="Queued for test",
            progress_percent=5
        )
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        test_id = analysis.id

    # Run pipeline with sample records
    records = [
        NormalizedRecord(
            platform="NEWS",
            raw_text="Samsung Galaxy S26 battery performance is outstanding, lasting two full days with heavy usage.",
            source_url="https://example.com/s26-review"
        ),
        NormalizedRecord(
            platform="NEWS",
            raw_text="The camera upgrade on Galaxy S26 takes stunning night photos. Highly recommended device.",
            source_url="https://example.com/s26-camera"
        ),
        NormalizedRecord(
            platform="NEWS",
            raw_text="Pricing is slightly steep for base model, but overall build and display are great.",
            source_url="https://example.com/s26-price"
        )
    ]

    await orchestrator.run_pipeline(test_id, preloaded_records=records)

    # Verify results in database
    async with AsyncSessionLocal() as db:
        res = await db.get(AnalysisRequest, test_id)
        assert res is not None
        assert res.status == AnalysisStatus.COMPLETED
        assert res.records_found == 3
        assert res.metrics is not None
        assert res.report is not None
        assert "Samsung" in res.report.report_title or "Galaxy" in res.report.report_title
        assert res.report.pdf_file_path is not None
