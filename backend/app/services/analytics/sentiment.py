from typing import List, Tuple
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from app.schemas.metrics import SentimentDistribution
from app.schemas.source import NormalizedRecord

class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()

    def score_text(self, text: str) -> float:
        """Returns the VADER compound polarity score for a single string (-1.0 to 1.0)."""
        scores = self.vader.polarity_scores(text)
        return scores["compound"]

    def analyze_records(self, records: List[NormalizedRecord]) -> Tuple[SentimentDistribution, List[float]]:
        """Calculates aggregate sentiment metrics and returns individual record scores."""
        if not records:
            return SentimentDistribution(
                positive=0.0,
                neutral=100.0,
                negative=0.0,
                average_compound_score=0.0,
                label="Neutral / No Data"
            ), []

        scores: List[float] = []
        pos_count = 0
        neu_count = 0
        neg_count = 0

        for r in records:
            text = r.cleaned_text or r.raw_text
            compound = self.score_text(text)
            scores.append(compound)
            
            if compound >= 0.05:
                pos_count += 1
            elif compound <= -0.05:
                neg_count += 1
            else:
                neu_count += 1

        total = len(records)
        pos_pct = (pos_count / total) * 100
        neu_pct = (neu_count / total) * 100
        neg_pct = (neg_count / total) * 100
        avg_score = sum(scores) / total

        # Determine qualitative label
        if avg_score >= 0.4:
            label = "Strongly Positive"
        elif avg_score >= 0.15:
            label = "Moderately Positive"
        elif avg_score >= 0.05:
            label = "Leaning Positive"
        elif avg_score <= -0.4:
            label = "Strongly Negative"
        elif avg_score <= -0.15:
            label = "Moderately Negative"
        elif avg_score <= -0.05:
            label = "Leaning Negative"
        else:
            label = "Neutral / Balanced"

        distribution = SentimentDistribution(
            positive=round(pos_pct, 1),
            neutral=round(neu_pct, 1),
            negative=round(neg_pct, 1),
            average_compound_score=round(avg_score, 3),
            label=label
        )

        return distribution, scores

sentiment_analyzer = SentimentAnalyzer()
