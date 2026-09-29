import logging
from typing import List
from app.schemas.metrics import AnalysisMetricsDTO
from app.schemas.source import NormalizedRecord
from app.services.analytics.preprocessor import preprocessor
from app.services.analytics.sentiment import sentiment_analyzer
from app.services.analytics.emotions import emotion_analyzer
from app.services.analytics.topics import topic_engine
from app.services.analytics.entities import entity_extractor
from app.services.analytics.trends import trend_analyzer
from app.services.analytics.forecasting import forecasting_engine

logger = logging.getLogger(__name__)

class QuantitativeAnalyticsEngine:
    def analyze(self, raw_records: List[NormalizedRecord]) -> AnalysisMetricsDTO:
        """Executes the full NLP & statistical pipeline over raw collected records."""
        
        # 1. Preprocessing & Deduplication
        cleaned_records = preprocessor.preprocess_records(raw_records)
        total_count = len(cleaned_records)
        logger.info(f"Analytics engine running on {total_count} cleaned records.")

        if total_count == 0:
            # Empty fallback
            sent_dist, scores = sentiment_analyzer.analyze_records([])
            return AnalysisMetricsDTO(
                total_records_analyzed=0,
                sentiment_distribution=sent_dist,
                emotion_scores=emotion_analyzer.analyze_records([]),
                topic_clusters=[],
                entity_mentions=[],
                time_series_trends=[],
                forecast_data=forecasting_engine.forecast([])
            )

        # 2. Sentiment Polarity Scoring
        sentiment_dist, sentiment_scores = sentiment_analyzer.analyze_records(cleaned_records)

        # 3. Emotion Scoring
        emotion_scores = emotion_analyzer.analyze_records(cleaned_records)

        # 4. Topic Extraction & Clustering
        topic_clusters = topic_engine.extract_topics(cleaned_records, sentiment_scores)

        # 5. Entity & Feature Frequency Analysis
        entity_mentions = entity_extractor.extract_entities(cleaned_records, sentiment_scores)

        # 6. Time-Series Trends
        time_series = trend_analyzer.compute_time_series(cleaned_records, sentiment_scores)

        # 7. Data-Driven Trend Forecasting
        forecast_result = forecasting_engine.forecast(time_series)

        return AnalysisMetricsDTO(
            total_records_analyzed=total_count,
            sentiment_distribution=sentiment_dist,
            emotion_scores=emotion_scores,
            topic_clusters=topic_clusters,
            entity_mentions=entity_mentions,
            time_series_trends=time_series,
            forecast_data=forecast_result
        )

analytics_engine = QuantitativeAnalyticsEngine()
