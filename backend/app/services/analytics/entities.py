import re
from collections import defaultdict
from typing import List
from app.schemas.metrics import EntityMentionItem
from app.schemas.source import NormalizedRecord

# Generic stopwords to exclude from entity detection
COMMON_WORDS = {
    "the", "and", "for", "with", "that", "this", "from", "they", "have", "been",
    "will", "what", "when", "where", "which", "more", "some", "also", "about",
    "into", "than", "then", "just", "like", "very", "much", "even", "only", "well"
}

class EntityExtractor:
    def __init__(self):
        # Matches Capitalized multi-word or single-word proper nouns
        self.proper_noun_pattern = re.compile(r'\b[A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+)*\b')
        
        # Domain aspect words
        self.aspect_words = [
            "battery", "camera", "display", "screen", "performance", "price", "cost", "value",
            "design", "build", "software", "update", "charging", "processor", "chip", "speed",
            "subsidy", "policy", "infrastructure", "government", "regulation", "incentive", "tax",
            "range", "mileage", "safety", "support", "warranty", "customer service"
        ]

    def extract_entities(
        self,
        records: List[NormalizedRecord],
        sentiment_scores: List[float],
        top_n: int = 10
    ) -> List[EntityMentionItem]:
        """Extracts top mentioned entities/aspects and calculates their sentiment polarity."""
        if not records:
            return []

        entity_counts = defaultdict(int)
        entity_sentiments = defaultdict(list)

        for idx, r in enumerate(records):
            text = r.cleaned_text or r.raw_text
            score = sentiment_scores[idx] if idx < len(sentiment_scores) else 0.0
            
            found_in_doc = set()

            # 1. Match proper nouns
            for match in self.proper_noun_pattern.finditer(text):
                ent = match.group(0).strip()
                if len(ent) > 2 and ent.lower() not in COMMON_WORDS:
                    found_in_doc.add(ent)

            # 2. Match aspect keywords
            text_lower = text.lower()
            for aspect in self.aspect_words:
                if re.search(rf'\b{aspect}\b', text_lower):
                    found_in_doc.add(aspect.title())

            for ent in found_in_doc:
                entity_counts[ent] += 1
                entity_sentiments[ent].append(score)

        # Build list
        items: List[EntityMentionItem] = []
        for ent, count in entity_counts.items():
            if count >= 1:
                avg_sent = sum(entity_sentiments[ent]) / len(entity_sentiments[ent])
                items.append(EntityMentionItem(
                    entity=ent,
                    count=count,
                    sentiment_score=round(avg_sent, 2)
                ))

        # Sort by mention frequency descending
        items.sort(key=lambda x: x.count, reverse=True)
        return items[:top_n]

entity_extractor = EntityExtractor()
