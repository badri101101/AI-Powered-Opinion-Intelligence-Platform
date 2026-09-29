import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.analysis import AnalysisRequest, AnalysisStatus
from app.models.source_data import SourceMetadata, CollectedRecord
from app.models.metrics import AnalysisMetrics
from app.models.report import GeneratedReport

from app.services.ai.input_analyzer import input_analyzer
from app.services.ai.report_writer import report_writer
from app.services.connectors.news_conn import news_connector
from app.services.connectors.reddit_conn import reddit_connector
from app.services.connectors.youtube_conn import youtube_connector
from app.services.analytics.engine import analytics_engine
from app.services.export.pdf_builder import pdf_builder

from app.schemas.source import NormalizedRecord, SourceMetadataDTO
from app.schemas.report import FullReportResponse, GeneratedReportDTO
from app.schemas.metrics import AnalysisMetricsDTO

logger = logging.getLogger(__name__)

class AnalysisOrchestrator:
    async def run_pipeline(
        self,
        analysis_id: uuid.UUID,
        preloaded_records: Optional[List[NormalizedRecord]] = None
    ) -> None:
        """Executes the asynchronous end-to-end opinion intelligence pipeline."""
        async with AsyncSessionLocal() as db:
            # 1. Fetch Analysis Request
            result = await db.execute(select(AnalysisRequest).where(AnalysisRequest.id == analysis_id))
            analysis = result.scalar_one_or_none()
            if not analysis:
                logger.error(f"Analysis {analysis_id} not found.")
                return

            try:
                # Stage 1: Classifying Request Intent (Gemini AI #1)
                analysis.status = AnalysisStatus.CLASSIFYING
                analysis.current_step = "Analyzing intent, category & source requirements..."
                analysis.progress_percent = 15
                await db.commit()

                intent = input_analyzer.analyze(analysis.original_prompt, analysis.category)
                analysis.category = intent.category
                analysis.target_entity = intent.target_entity
                analysis.location_scope = intent.location_scope
                analysis.time_period_days = intent.time_period_days
                analysis.intent_parameters = intent.model_dump()
                await db.commit()

                # Stage 2: Data Collection
                analysis.status = AnalysisStatus.COLLECTING
                analysis.current_step = "Harvesting discussions across verified platforms..."
                analysis.progress_percent = 35
                await db.commit()

                all_records: List[NormalizedRecord] = []
                source_meta_rows: List[SourceMetadata] = []

                if preloaded_records:
                    # Dataset file upload scenario
                    all_records.extend(preloaded_records)
                    source_meta = SourceMetadata(
                        id=uuid.uuid4(),
                        analysis_id=analysis.id,
                        platform="FILE_UPLOAD",
                        source_url=preloaded_records[0].source_url if preloaded_records else "Uploaded Dataset",
                        query_used=analysis.original_prompt,
                        records_collected=len(preloaded_records),
                        status="SUCCESS",
                        fetched_at=datetime.now(timezone.utc)
                    )
                    db.add(source_meta)
                    source_meta_rows.append(source_meta)
                else:
                    # Multi-source harvesting
                    queries = intent.source_queries
                    time_days = intent.time_period_days

                    # 1. News/RSS Collection
                    news_q = queries.news_query or intent.target_entity or analysis.original_prompt
                    news_records = await news_connector.collect(news_q, limit=40, time_days=time_days, url=intent.url_target)
                    all_records.extend(news_records)
                    news_meta = SourceMetadata(
                        id=uuid.uuid4(),
                        analysis_id=analysis.id,
                        platform="NEWS",
                        source_url="https://news.google.com/rss",
                        query_used=news_q,
                        records_collected=len(news_records),
                        status="SUCCESS" if news_records else "EMPTY",
                        fetched_at=datetime.now(timezone.utc)
                    )
                    db.add(news_meta)
                    source_meta_rows.append(news_meta)

                    # 2. Reddit API Collection
                    if reddit_connector.is_configured() or (intent.url_target and "reddit.com" in intent.url_target):
                        reddit_q = queries.reddit_query or intent.target_entity or analysis.original_prompt
                        reddit_records = await reddit_connector.collect(reddit_q, limit=40, time_days=time_days, url=intent.url_target)
                        all_records.extend(reddit_records)
                        reddit_meta = SourceMetadata(
                            id=uuid.uuid4(),
                            analysis_id=analysis.id,
                            platform="REDDIT",
                            source_url=intent.url_target if intent.url_target and "reddit.com" in intent.url_target else "https://reddit.com",
                            query_used=reddit_q,
                            records_collected=len(reddit_records),
                            status="SUCCESS" if reddit_records else "EMPTY",
                            fetched_at=datetime.now(timezone.utc)
                        )
                        db.add(reddit_meta)
                        source_meta_rows.append(reddit_meta)

                    # 3. YouTube API Collection
                    if youtube_connector.is_configured() or (intent.url_target and "youtu" in intent.url_target):
                        yt_q = queries.youtube_query or intent.target_entity or analysis.original_prompt
                        yt_records = await youtube_connector.collect(yt_q, limit=40, time_days=time_days, url=intent.url_target)
                        all_records.extend(yt_records)
                        yt_meta = SourceMetadata(
                            id=uuid.uuid4(),
                            analysis_id=analysis.id,
                            platform="YOUTUBE",
                            source_url=intent.url_target if intent.url_target and "youtu" in intent.url_target else "https://youtube.com",
                            query_used=yt_q,
                            records_collected=len(yt_records),
                            status="SUCCESS" if yt_records else "EMPTY",
                            fetched_at=datetime.now(timezone.utc)
                        )
                        db.add(yt_meta)
                        source_meta_rows.append(yt_meta)

                # Persist collected records
                for rec in all_records:
                    db_record = CollectedRecord(
                        id=uuid.uuid4(),
                        analysis_id=analysis.id,
                        platform=rec.platform,
                        external_id=rec.external_id,
                        raw_text=rec.raw_text,
                        cleaned_text=rec.cleaned_text,
                        author=rec.author,
                        published_at=rec.published_at,
                        engagement_score=rec.engagement_score,
                        source_url=rec.source_url,
                        record_metadata=rec.metadata,
                        created_at=datetime.now(timezone.utc)
                    )
                    db.add(db_record)

                analysis.records_found = len(all_records)
                await db.commit()

                # Stage 3: Quantitative NLP & Statistical Analysis
                analysis.status = AnalysisStatus.ANALYZING
                analysis.current_step = "Computing sentiment, thematic clusters & trend velocity..."
                analysis.progress_percent = 65
                await db.commit()

                metrics_dto: AnalysisMetricsDTO = analytics_engine.analyze(all_records)
                
                db_metrics = AnalysisMetrics(
                    id=uuid.uuid4(),
                    analysis_id=analysis.id,
                    total_records_analyzed=metrics_dto.total_records_analyzed,
                    sentiment_distribution=metrics_dto.sentiment_distribution.model_dump(),
                    emotion_scores=metrics_dto.emotion_scores.model_dump(),
                    topic_clusters=[t.model_dump() for t in metrics_dto.topic_clusters],
                    entity_mentions=[e.model_dump() for e in metrics_dto.entity_mentions],
                    time_series_trends=[pt.model_dump() for pt in metrics_dto.time_series_trends],
                    forecast_data=metrics_dto.forecast_data.model_dump(),
                    computed_at=datetime.now(timezone.utc)
                )
                db.add(db_metrics)
                await db.commit()

                # Stage 4: Narrative Report Synthesis (Gemini AI #2) & PDF Export
                analysis.status = AnalysisStatus.GENERATING
                analysis.current_step = "Generating evidence-grounded report & publication PDF..."
                analysis.progress_percent = 85
                await db.commit()

                source_dtos = [
                    SourceMetadataDTO(
                        id=s.id,
                        platform=s.platform,
                        source_url=s.source_url,
                        query_used=s.query_used,
                        records_collected=s.records_collected,
                        status=s.status,
                        error_message=s.error_message,
                        fetched_at=s.fetched_at or datetime.now(timezone.utc)
                    )
                    for s in source_meta_rows
                ]

                report_spec = report_writer.generate_report(
                    original_prompt=analysis.original_prompt,
                    intent=intent,
                    metrics=metrics_dto,
                    sources=source_dtos
                )

                # Assemble Full Report DTO for PDF generator
                report_dto = GeneratedReportDTO(
                    report_title=report_spec.report_title,
                    executive_summary=report_spec.executive_summary,
                    key_findings=report_spec.key_findings,
                    topic_summaries=report_spec.topic_summaries,
                    trend_narrative=report_spec.trend_narrative,
                    forecast_interpretation=report_spec.forecast_interpretation,
                    caveats_and_disclaimers=report_spec.caveats_and_disclaimers,
                    generated_at=datetime.now(timezone.utc)
                )

                full_report_dto = FullReportResponse(
                    id=analysis.id,
                    original_prompt=analysis.original_prompt,
                    category=analysis.category,
                    target_entity=analysis.target_entity,
                    location_scope=analysis.location_scope,
                    time_period_days=analysis.time_period_days,
                    status=AnalysisStatus.COMPLETED,
                    created_at=analysis.created_at,
                    completed_at=datetime.now(timezone.utc),
                    report=report_dto,
                    metrics=metrics_dto,
                    sources=source_dtos,
                    records_found=len(all_records)
                )

                # Generate PDF document
                pdf_path = pdf_builder.generate_pdf(full_report_dto)
                report_dto.pdf_file_path = pdf_path

                db_report = GeneratedReport(
                    id=uuid.uuid4(),
                    analysis_id=analysis.id,
                    report_title=report_spec.report_title,
                    executive_summary=report_spec.executive_summary,
                    key_findings=[f.model_dump() for f in report_spec.key_findings],
                    topic_summaries=[t.model_dump() for t in report_spec.topic_summaries],
                    trend_narrative=report_spec.trend_narrative,
                    forecast_interpretation=report_spec.forecast_interpretation,
                    caveats_and_disclaimers=report_spec.caveats_and_disclaimers,
                    pdf_file_path=pdf_path,
                    generated_at=datetime.now(timezone.utc)
                )
                db.add(db_report)

                # Stage 5: Completion
                analysis.status = AnalysisStatus.COMPLETED
                analysis.current_step = "Analysis completed successfully"
                analysis.progress_percent = 100
                analysis.completed_at = datetime.now(timezone.utc)
                await db.commit()
                logger.info(f"Analysis {analysis_id} completed successfully.")

            except Exception as e:
                logger.exception(f"Pipeline error on analysis {analysis_id}: {e}")
                try:
                    await db.rollback()
                    analysis.status = AnalysisStatus.FAILED
                    analysis.current_step = "Execution failed"
                    analysis.error_message = str(e)
                    analysis.completed_at = datetime.now(timezone.utc)
                    await db.commit()
                except Exception as rollback_err:
                    logger.error(f"Failed to update error status for analysis {analysis_id}: {rollback_err}")

orchestrator = AnalysisOrchestrator()
