import os
import uuid
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.models.analysis import AnalysisRequest, AnalysisStatus
from app.models.report import GeneratedReport
from app.models.metrics import AnalysisMetrics
from app.models.source_data import SourceMetadata
from app.schemas.report import FullReportResponse, GeneratedReportDTO
from app.schemas.metrics import AnalysisMetricsDTO
from app.schemas.source import SourceMetadataDTO
from app.services.export.pdf_builder import pdf_builder

router = APIRouter()

@router.get("/{analysis_id}/export/pdf")
async def export_pdf_report(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    """Generates and streams the publication-ready PDF report document."""
    result = await db.execute(select(AnalysisRequest).where(AnalysisRequest.id == analysis_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    if analysis.status != AnalysisStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Analysis is still in progress or failed.")

    report_res = await db.execute(select(GeneratedReport).where(GeneratedReport.analysis_id == analysis_id))
    db_report = report_res.scalar_one_or_none()

    if db_report and db_report.pdf_file_path and os.path.exists(db_report.pdf_file_path):
        return FileResponse(
            path=db_report.pdf_file_path,
            filename=f"opinion_report_{analysis_id}.pdf",
            media_type="application/pdf"
        )

    # Re-generate PDF if missing on disk
    metrics_res = await db.execute(select(AnalysisMetrics).where(AnalysisMetrics.analysis_id == analysis_id))
    db_metrics = metrics_res.scalar_one_or_none()

    sources_res = await db.execute(select(SourceMetadata).where(SourceMetadata.analysis_id == analysis_id))
    db_sources = sources_res.scalars().all()

    report_dto = GeneratedReportDTO(
        report_title=db_report.report_title if db_report else f"Opinion Report: {analysis.target_entity}",
        executive_summary=db_report.executive_summary if db_report else "",
        key_findings=db_report.key_findings if db_report else [],
        topic_summaries=db_report.topic_summaries if db_report else [],
        trend_narrative=db_report.trend_narrative if db_report else "",
        forecast_interpretation=db_report.forecast_interpretation if db_report else None,
        caveats_and_disclaimers=db_report.caveats_and_disclaimers if db_report else "",
        generated_at=db_report.generated_at if db_report else analysis.created_at
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

    full_dto = FullReportResponse(
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

    pdf_path = pdf_builder.generate_pdf(full_dto)
    if db_report:
        db_report.pdf_file_path = pdf_path
        await db.commit()

    return FileResponse(
        path=pdf_path,
        filename=f"opinion_report_{analysis_id}.pdf",
        media_type="application/pdf"
    )
