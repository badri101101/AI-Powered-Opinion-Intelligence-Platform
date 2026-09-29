from collections import defaultdict
from datetime import datetime, timezone
from typing import List
from app.schemas.metrics import TimeSeriesPoint
from app.schemas.source import NormalizedRecord

class TrendAnalyzer:
    def compute_time_series(
        self,
        records: List[NormalizedRecord],
        sentiment_scores: List[float]
    ) -> List[TimeSeriesPoint]:
        """Aggregates record counts and average sentiment by publication date."""
        if not records:
            return []

        date_groups = defaultdict(lambda: {"count": 0, "scores": []})

        for idx, r in enumerate(records):
            score = sentiment_scores[idx] if idx < len(sentiment_scores) else 0.0
            dt = r.published_at or datetime.now(timezone.utc)
            date_key = dt.strftime("%Y-%m-%d")
            
            date_groups[date_key]["count"] += 1
            date_groups[date_key]["scores"].append(score)

        # Sort dates chronologically
        sorted_dates = sorted(date_groups.keys())

        time_series: List[TimeSeriesPoint] = []
        for d in sorted_dates:
            data = date_groups[d]
            avg_score = sum(data["scores"]) / data["count"] if data["count"] > 0 else 0.0
            time_series.append(TimeSeriesPoint(
                date=d,
                count=data["count"],
                sentiment_score=round(avg_score, 2)
            ))

        return time_series

trend_analyzer = TrendAnalyzer()
