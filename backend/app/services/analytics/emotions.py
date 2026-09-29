import re
from typing import List, Dict
from app.schemas.metrics import EmotionScores
from app.schemas.source import NormalizedRecord

# Curated emotion lexicons for opinion intelligence
EMOTION_LEXICON: Dict[str, List[str]] = {
    "joy": [
        "great", "excellent", "love", "amazing", "awesome", "good", "best", "happy", "perfect",
        "fantastic", "smooth", "impressive", "brilliant", "enjoy", "satisfied", "pleased",
        "superb", "flawless", "wonderful", "top", "outstanding", "favorite", "favourite"
    ],
    "anger": [
        "terrible", "worst", "hate", "awful", "scam", "horrible", "annoying", "angry", "ridiculous",
        "useless", "broken", "garbage", "trash", "bad", "sucks", "disaster", "fail", "failed",
        "fraud", "rip off", "waste", "corrupt", "unacceptable", "furious", "poor"
    ],
    "sadness": [
        "disappointed", "sad", "unfortunate", "regret", "miss", "pity", "lacks", "lost", "missing",
        "downgrade", "flaw", "shame", "poor", "unhappy", "depressing", "grief", "sorrow", "downside"
    ],
    "trust": [
        "reliable", "secure", "trust", "solid", "durable", "consistent", "authentic", "official",
        "guaranteed", "recommended", "safe", "stable", "accurate", "tested", "proven", "honest"
    ],
    "surprise": [
        "unexpected", "surprise", "surprised", "shocking", "unbelievable", "wow", "suddenly",
        "curious", "unusual", "novel", "game changer", "revolutionary", "innovative", "unforeseen"
    ]
}

class EmotionAnalyzer:
    def __init__(self):
        # Precompile word boundary regex patterns for fast matching
        self.patterns = {
            emotion: [re.compile(rf'\b{re.escape(w)}\b', re.IGNORECASE) for w in words]
            for emotion, words in EMOTION_LEXICON.items()
        }

    def analyze_records(self, records: List[NormalizedRecord]) -> EmotionScores:
        """Computes normalized emotion intensity scores across the collected text records."""
        if not records:
            return EmotionScores()

        counts = {"joy": 0, "anger": 0, "sadness": 0, "trust": 0, "surprise": 0}
        total_matches = 0

        for r in records:
            text = (r.cleaned_text or r.raw_text).lower()
            for emotion, regex_list in self.patterns.items():
                for pat in regex_list:
                    if pat.search(text):
                        counts[emotion] += 1
                        total_matches += 1

        if total_matches == 0:
            return EmotionScores(joy=20.0, anger=20.0, sadness=20.0, trust=20.0, surprise=20.0)

        return EmotionScores(
            joy=round((counts["joy"] / total_matches) * 100, 1),
            anger=round((counts["anger"] / total_matches) * 100, 1),
            sadness=round((counts["sadness"] / total_matches) * 100, 1),
            trust=round((counts["trust"] / total_matches) * 100, 1),
            surprise=round((counts["surprise"] / total_matches) * 100, 1)
        )

emotion_analyzer = EmotionAnalyzer()
