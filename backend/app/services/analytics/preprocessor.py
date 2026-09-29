import re
import html
from typing import List
from app.schemas.source import NormalizedRecord

class TextPreprocessor:
    def __init__(self):
        self.url_pattern = re.compile(r'https?://\S+|www\.\S+')
        self.html_tag_pattern = re.compile(r'<[^>]+>')
        self.whitespace_pattern = re.compile(r'\s+')

    def clean_text(self, text: str) -> str:
        """Sanitizes raw comment/review text for statistical NLP processing."""
        if not text:
            return ""
        
        # Unescape HTML
        text = html.unescape(text)
        
        # Remove URLs
        text = self.url_pattern.sub('', text)
        
        # Remove HTML tags
        text = self.html_tag_pattern.sub('', text)
        
        # Normalize whitespace
        text = self.whitespace_pattern.sub(' ', text).strip()
        
        return text

    def preprocess_records(self, records: List[NormalizedRecord]) -> List[NormalizedRecord]:
        """Cleans and deduplicates raw records."""
        processed: List[NormalizedRecord] = []
        seen_texts = set()

        for record in records:
            cleaned = self.clean_text(record.raw_text)
            if not cleaned or len(cleaned) < 5:
                continue

            # Deduplication key
            dedup_key = cleaned.lower()[:120]
            if dedup_key in seen_texts:
                continue
            
            seen_texts.add(dedup_key)
            record.cleaned_text = cleaned
            processed.append(record)

        return processed

preprocessor = TextPreprocessor()
