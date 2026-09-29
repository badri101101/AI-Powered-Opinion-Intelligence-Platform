import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.database import get_db
from app.models.analysis import AnalysisRequest, AnalysisStatus
from app.models.source_data import SourceMetadata
from app.models.metrics import AnalysisMetrics
from app.models.report import GeneratedReport
from app.schemas.analysis import (
    AnalysisCreate, AnalysisStatusResponse, AnalysisListItem, AnalysisListResponse
)
from app.schemas.report import FullReportResponse, GeneratedReportDTO
from app.schemas.metrics import AnalysisMetricsDTO
from app.schemas.source import SourceMetadataDTO
from app.services.orchestrator import orchestrator
from app.services.connectors.file_conn import file_connector

router = APIRouter()

@router.post("", response_model=AnalysisStatusResponse, status_code=202)
async def create_analysis(
    payload: AnalysisCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Initiates a new multi-source opinion intelligence analysis run."""
    prompt_text = payload.prompt.strip()
    if not prompt_text:
        raise HTTPException(status_code=400, detail="Analysis prompt cannot be empty.")

    analysis = AnalysisRequest(
        original_prompt=prompt_text,
        category=payload.category_override,
        status=AnalysisStatus.PENDING,
        current_step="Queued for analysis...",
        progress_percent=5
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    # Launch background asynchronous pipeline
    background_tasks.add_task(orchestrator.run_pipeline, analysis.id)

    return AnalysisStatusResponse(
        id=analysis.id,
        status=analysis.status,
        current_step=analysis.current_step,
        progress_percent=analysis.progress_percent,
        records_found=0,
        completed_at=None
    )

@router.post("/upload", response_model=AnalysisStatusResponse, status_code=202)
async def upload_dataset_analysis(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    prompt: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Uploads a CSV or Excel dataset and initiates automated opinion intelligence analysis."""
    if not file.filename.lower().endswith((".csv", ".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Only CSV (.csv) and Excel (.xlsx, .xls) files are supported.")

    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    records, err = file_connector.parse_file(file_bytes, file.filename)
    if err:
        raise HTTPException(status_code=400, detail=err)

    analysis_prompt = prompt.strip() if (prompt and prompt.strip()) else f"Analyze uploaded dataset: {file.filename}"

    analysis = AnalysisRequest(
        original_prompt=analysis_prompt,
        category="DATASET",
        target_entity=file.filename,
        status=AnalysisStatus.PENDING,
        current_step="Dataset uploaded. Preparing analysis...",
        progress_percent=5,
        records_found=len(records)
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    # Launch background pipeline with preloaded records
    background_tasks.add_task(orchestrator.run_pipeline, analysis.id, records)

    return AnalysisStatusResponse(
        id=analysis.id,
        status=analysis.status,
        current_step=analysis.current_step,
        progress_percent=analysis.progress_percent,
        records_found=len(records),
        completed_at=None
    )

@router.get("/{analysis_id}/status", response_model=AnalysisStatusResponse)
async def get_analysis_status(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Polling endpoint for real-time analysis progress and execution state."""
    result = await db.execute(select(AnalysisRequest).where(AnalysisRequest.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis request not found.")

    return AnalysisStatusResponse(
        id=analysis.id,
        status=analysis.status,
        current_step=analysis.current_step,
        progress_percent=analysis.progress_percent,
        records_found=analysis.records_found,
        error_message=analysis.error_message,
        completed_at=analysis.completed_at
    )

@router.get("/{analysis_id}/report", response_model=FullReportResponse)
async def get_analysis_report(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Retrieves the complete consolidated intelligence dashboard report."""
    result = await db.execute(select(AnalysisRequest).where(AnalysisRequest.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    if analysis.status != AnalysisStatus.COMPLETED:
        raise HTTPException(
            status_code=400,
            detail=f"Report is not ready yet. Current status: {analysis.status} ({analysis.current_step})"
        )

    # Fetch nested metrics, report, and sources
    metrics_res = await db.execute(select(AnalysisMetrics).where(AnalysisMetrics.analysis_id == analysis_id))
    db_metrics = metrics_res.scalar_one_or_none()

    report_res = await db.execute(select(GeneratedReport).where(GeneratedReport.analysis_id == analysis_id))
    db_report = report_res.scalar_one_or_none()

    sources_res = await db.execute(select(SourceMetadata).where(SourceMetadata.analysis_id == analysis_id))
    db_sources = sources_res.scalars().all()

    report_dto = None
    if db_report:
        report_dto = GeneratedReportDTO(
            id=db_report.id,
            report_title=db_report.report_title,
            executive_summary=db_report.executive_summary,
            key_findings=db_report.key_findings,
            topic_summaries=db_report.topic_summaries,
            trend_narrative=db_report.trend_narrative,
            forecast_interpretation=db_report.forecast_interpretation,
            caveats_and_disclaimers=db_report.caveats_and_disclaimers,
            pdf_file_path=db_report.pdf_file_path,
            generated_at=db_report.generated_at
        )

    metrics_dto = None
    if db_metrics:
        metrics_dto = AnalysisMetricsDTO(
            total_records_analyzed=db_metrics.total_records_analyzed,
            sentiment_distribution=db_metrics.sentiment_distribution,
            emotion_scores=db_metrics.emotion_scores,
            topic_clusters=db_metrics.topic_clusters,
            entity_mentions=db_metrics.entity_mentions,
            time_series_trends=db_metrics.time_series_trends,
            forecast_data=db_metrics.forecast_data
        )

    source_dtos = [
        SourceMetadataDTO(
            id=s.id,
            platform=s.platform,
            source_url=s.source_url,
            query_used=s.query_used,
            records_collected=s.records_collected,
            status=s.status,
            error_message=s.error_message,
            fetched_at=s.fetched_at
        )
        for s in db_sources
    ]

    return FullReportResponse(
        id=analysis.id,
        original_prompt=analysis.original_prompt,
        category=analysis.category,
        target_entity=analysis.target_entity,
        location_scope=analysis.location_scope,
        time_period_days=analysis.time_period_days,
        status=analysis.status,
        created_at=analysis.created_at,
        completed_at=analysis.completed_at,
        report=report_dto,
        metrics=metrics_dto,
        sources=source_dtos,
        records_found=analysis.records_found
    )

@router.get("", response_model=AnalysisListResponse)
async def list_analyses(
    limit: int = 15,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Lists recent analysis sessions."""
    result = await db.execute(
        select(AnalysisRequest)
        .order_by(desc(AnalysisRequest.created_at))
        .limit(limit)
        .offset(offset)
    )
    items = result.scalars().all()
    
    return AnalysisListResponse(
        items=[AnalysisListItem.model_validate(item) for item in items],
        total=len(items)
    )
