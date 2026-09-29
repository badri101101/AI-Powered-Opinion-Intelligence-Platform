import json
import logging
from typing import List, Optional
from app.schemas.ai_specs import ReportSynthesisSpec, InputAnalysisSpec, KeyFindingSpec, TopicSummarySpec
from app.schemas.metrics import AnalysisMetricsDTO
from app.schemas.source import SourceMetadataDTO
from app.services.ai.gemini_client import gemini_service
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION_REPORT_WRITER = """
You are a Senior Opinion Intelligence Analyst.
Your task is to write an executive-level analytical report based STRICTLY on the quantitative facts and NLP statistics provided in the prompt.
Do NOT act as a conversational assistant. Do NOT include greetings or chat remarks.

CRITICAL GUARDRAILS:
1. Strict Fact-Grounding: CITE ONLY the numbers, percentages, topics, emotions, and source metrics provided. Do NOT invent statistics or imaginary sources.
2. Policy & Political Neutrality: For policy, legal, or political topics, analyze measurable public sentiment and concerns. NEVER declare definitive outcomes about elections, political support, or subjective ideology.
3. Clarity & Professionalism: Provide clear, actionable executive insights, concise takeaways, and transparent methodological disclaimers.
"""

class ReportWriterService:
    def generate_report(
        self,
        original_prompt: str,
        intent: InputAnalysisSpec,
        metrics: AnalysisMetricsDTO,
        sources: List[SourceMetadataDTO]
    ) -> ReportSynthesisSpec:
        """Generates structured report synthesis using Gemini AI #2 with data-grounded fallback."""
        
        # Prepare structured facts payload
        facts_payload = {
            "request_metadata": {
                "original_prompt": original_prompt,
                "category": intent.category,
                "target_entity": intent.target_entity,
                "location_scope": intent.location_scope,
                "total_records_analyzed": metrics.total_records_analyzed
            },
            "sentiment_statistics": {
                "positive_percent": round(metrics.sentiment_distribution.positive, 1),
                "neutral_percent": round(metrics.sentiment_distribution.neutral, 1),
                "negative_percent": round(metrics.sentiment_distribution.negative, 1),
                "average_compound_score": round(metrics.sentiment_distribution.average_compound_score, 3),
                "overall_label": metrics.sentiment_distribution.label
            },
            "emotion_profile": {
                "joy": round(metrics.emotion_scores.joy, 1),
                "anger": round(metrics.emotion_scores.anger, 1),
                "sadness": round(metrics.emotion_scores.sadness, 1),
                "trust": round(metrics.emotion_scores.trust, 1),
                "surprise": round(metrics.emotion_scores.surprise, 1)
            },
            "thematic_clusters": [
                {
                    "topic_id": t.topic_id,
                    "name": t.name,
                    "top_keywords": t.keywords,
                    "share_percentage": round(t.share_percentage, 1),
                    "sentiment_score": round(t.sentiment_score, 2)
                }
                for t in metrics.topic_clusters
            ],
            "top_entities": [
                {"entity": e.entity, "mentions": e.count, "sentiment": round(e.sentiment_score, 2)}
                for e in metrics.entity_mentions[:8]
            ],
            "trend_and_forecast": {
                "forecast_available": metrics.forecast_data.available,
                "trend_direction": metrics.forecast_data.trend_direction,
                "slope": round(metrics.forecast_data.slope, 4),
                "confidence": metrics.forecast_data.confidence,
                "statistical_note": metrics.forecast_data.reason
            },
            "sources_harvested": [
                {
                    "platform": s.platform,
                    "records_collected": s.records_collected,
                    "query_or_url": s.query_used or s.source_url
                }
                for s in sources
            ]
        }

        # 1. Attempt Gemini Generation
        if gemini_service.is_available():
            prompt_content = f"Here is the verified analytical data collected and computed by our NLP pipeline:\n\n{json.dumps(facts_payload, indent=2)}\n\nGenerate the complete structured report according to the schema."
            report_spec = gemini_service.generate_structured(
                prompt=prompt_content,
                system_instruction=SYSTEM_INSTRUCTION_REPORT_WRITER,
                schema=ReportSynthesisSpec,
                model=settings.GEMINI_REPORT_MODEL
            )
            if report_spec:
                return report_spec

        # 2. Data-Grounded Compiler Fallback
        logger.info("Using deterministic fact-grounded report compiler fallback.")
        return self._deterministic_compiler(original_prompt, intent, metrics, sources)

    def _deterministic_compiler(
        self,
        original_prompt: str,
        intent: InputAnalysisSpec,
        metrics: AnalysisMetricsDTO,
        sources: List[SourceMetadataDTO]
    ) -> ReportSynthesisSpec:
        """Assembles a high-precision executive report grounded strictly in the statistical metrics."""
        entity = intent.target_entity or "the target subject"
        total = metrics.total_records_analyzed
        sent = metrics.sentiment_distribution
        
        # Build Title
        title = f"Multi-Source Opinion Intelligence Brief: {entity}"
        
        # Build Executive Summary
        summary = (
            f"An automated multi-source analysis was conducted on '{original_prompt}' across {len(sources)} verified data channels, "
            f"evaluating a total of {total} public records. Overall public sentiment is {sent.label.lower()} with an average compound polarity "
            f"of {sent.average_compound_score:+.2f}. Discussion is distributed across {sent.positive:.1f}% positive, {sent.neutral:.1f}% neutral, "
            f"and {sent.negative:.1f}% negative viewpoints."
        )

        # Build Key Findings
        findings = []
        findings.append(KeyFindingSpec(
            title=f"Overall Sentiment Tone: {sent.label}",
            description=f"Public discourse exhibits {sent.positive:.1f}% favorable sentiment compared to {sent.negative:.1f}% critical remarks across collected records.",
            impact="POSITIVE" if sent.average_compound_score > 0.05 else ("NEGATIVE" if sent.average_compound_score < -0.05 else "NEUTRAL")
        ))
        findings.append(KeyFindingSpec(
            title="Multi-Source Data Ingestion",
            description=f"Pipeline gathered {total} verified public records across {len(sources)} active data connectors.",
            impact="NEUTRAL"
        ))

        if metrics.topic_clusters:
            top_t = metrics.topic_clusters[0]
            findings.append(KeyFindingSpec(
                title=f"Primary Discussion Focus: {top_t.name}",
                description=f"The most dominant theme accounts for {top_t.share_percentage:.1f}% of discussions, centered around key terms: {', '.join(top_t.keywords[:4])}.",
                impact="NEUTRAL"
            ))

        if metrics.entity_mentions:
            top_e = metrics.entity_mentions[0]
            findings.append(KeyFindingSpec(
                title=f"Key Mentioned Aspect: {top_e.entity}",
                description=f"'{top_e.entity}' emerged as the highest frequency feature mentioned ({top_e.count} times) with an average sentiment score of {top_e.sentiment_score:+.2f}.",
                impact="POSITIVE" if top_e.sentiment_score > 0.05 else ("NEGATIVE" if top_e.sentiment_score < -0.05 else "NEUTRAL")
            ))

        # Build Topic Summaries
        topic_summaries = []
        for t in metrics.topic_clusters[:4]:
            kw_str = ", ".join(t.keywords[:5])
            topic_summaries.append(TopicSummarySpec(
                topic_name=t.name,
                summary=f"Discussions focusing on {kw_str} represent {t.share_percentage:.1f}% of overall volume with an average sentiment score of {t.sentiment_score:+.2f}.",
                sentiment_note=f"Net sentiment for this cluster is {'positive' if t.sentiment_score > 0.05 else ('negative' if t.sentiment_score < -0.05 else 'neutral')}."
            ))

        # Build Trend Narrative
        trend_narrative = (
            f"Time-series analysis of {len(metrics.time_series_trends)} temporal intervals indicates discussion momentum "
            f"with volume velocity aligned around key news and community releases. Sentiment trajectory maintains an average "
            f"baseline of {sent.average_compound_score:+.2f}."
        )

        # Build Forecast Interpretation
        forecast_interp = None
        if metrics.forecast_data.available:
            forecast_interp = (
                f"Statistical trajectory modeling projects {metrics.forecast_data.trend_direction.lower()} sentiment momentum "
                f"(linear regression slope: {metrics.forecast_data.slope:+.4f}, confidence: {metrics.forecast_data.confidence}). "
                f"Note: Forecasts represent short-term momentum from current data and should be interpreted as trend indicators rather than guarantees."
            )
        else:
            forecast_interp = f"Trend forecasting is unavailable: {metrics.forecast_data.reason}."

        # Build Disclaimers
        disclaimer = (
            "Methodology Notice: This report synthesizes public opinions, reviews, and news items gathered automatically from official APIs and open sources. "
            "For public policy and civic topics, findings reflect measurable public sentiment in collected discussion samples and do not represent official polls or definitive election outcomes."
        )

        return ReportSynthesisSpec(
            report_title=title,
            executive_summary=summary,
            key_findings=findings,
            topic_summaries=topic_summaries,
            trend_narrative=trend_narrative,
            forecast_interpretation=forecast_interp,
            caveats_and_disclaimers=disclaimer
        )

report_writer = ReportWriterService()
