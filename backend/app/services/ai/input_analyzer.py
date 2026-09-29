import re
import logging
from typing import Optional
from app.schemas.ai_specs import InputAnalysisSpec, SourceQuerySpec
from app.services.ai.gemini_client import gemini_service
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION_ANALYZER = """
You are an expert NLP Workflow Classifier and Intent Analyzer for a multi-source intelligence platform.
Your ONLY role is to analyze the user's input request and return a structured specification JSON conforming to the schema.
DO NOT generate any opinion, report, or summary of the topic.

Rules:
1. Classify category into ONE of:
   - "PRODUCT": Requests analyzing consumer products, smartphones, software, gadgets, cars, hardware, reviews, comparisons.
   - "POLICY": Requests analyzing government policies, bills, laws, subsidies, elections, public schemes, civic regulations.
   - "TOPIC": Broad themes, cultural or industry trends, public discussions, concepts.
   - "URL": Direct links to Reddit posts/threads, YouTube videos, or articles.
   - "DATASET": References to uploaded files or structured data.
2. Extract the clean 'target_entity' (e.g. "Samsung Galaxy S26", "EV Subsidy Policy in India", "Electric Vehicles").
3. Determine 'location_scope' if mentioned or clearly implied (e.g. "India", "USA", "Global").
4. Select appropriate 'recommended_sources' from ["REDDIT", "YOUTUBE", "NEWS", "FILE_UPLOAD"].
5. Generate optimized search queries in 'source_queries' for each connector.
"""

class InputAnalyzerService:
    def analyze(self, prompt: str, category_override: Optional[str] = None) -> InputAnalysisSpec:
        """Analyzes natural-language user prompt using Gemini AI #1 with deterministic fallback."""
        prompt_clean = prompt.strip()

        # 1. Attempt Gemini Structured Classification
        if gemini_service.is_available():
            user_msg = f"User Request: \"{prompt_clean}\"\n"
            if category_override:
                user_msg += f"User specified category override: {category_override}\n"

            spec = gemini_service.generate_structured(
                prompt=user_msg,
                system_instruction=SYSTEM_INSTRUCTION_ANALYZER,
                schema=InputAnalysisSpec,
                model=settings.GEMINI_ANALYZER_MODEL
            )
            if spec:
                if category_override and category_override in ["PRODUCT", "POLICY", "TOPIC", "URL", "DATASET"]:
                    spec.category = category_override
                return spec

        # 2. Heuristic Rule-Based Fallback (if Gemini unavailable or offline)
        logger.info("Using heuristic intent analyzer fallback.")
        return self._heuristic_fallback(prompt_clean, category_override)

    def _heuristic_fallback(self, prompt: str, category_override: Optional[str] = None) -> InputAnalysisSpec:
        prompt_lower = prompt.lower()
        url_match = re.search(r'https?://[^\s]+', prompt)
        
        category = "TOPIC"
        url_target = None
        target_entity = prompt
        location = "Global"

        # Check for direct URL
        if url_match:
            category = "URL"
            url_target = url_match.group(0)
            target_entity = url_target
        elif any(w in prompt_lower for for_word in ["policy", "subsidy", "bill", "law", "government", "scheme", "regulation", "tax", "election", "minister", "budget"] if (w := for_word) in prompt_lower):
            category = "POLICY"
        elif any(w in prompt_lower for for_word in ["review", "specs", "vs", "phone", "galaxy", "iphone", "laptop", "camera", "battery", "price", "s24", "s25", "s26", "pixel", "macbook", "edition"] if (w := for_word) in prompt_lower):
            category = "PRODUCT"
        elif "dataset" in prompt_lower or "upload" in prompt_lower or "csv" in prompt_lower:
            category = "DATASET"

        if category_override and category_override in ["PRODUCT", "POLICY", "TOPIC", "URL", "DATASET"]:
            category = category_override

        # Detect Location
        if "india" in prompt_lower:
            location = "India"
        elif "us" in prompt_lower or "usa" in prompt_lower or "america" in prompt_lower:
            location = "United States"
        elif "uk" in prompt_lower or "britain" in prompt_lower:
            location = "United Kingdom"
        elif "europe" in prompt_lower or "eu" in prompt_lower:
            location = "Europe"

        # Clean target entity
        clean_name = re.sub(r'^(analyze|analyse|what is public opinion on|public opinion about|reviews of|discussions about|analyze this)\s+', '', prompt, flags=re.IGNORECASE).strip()
        if clean_name and len(clean_name) > 1:
            target_entity = clean_name

        query_term = target_entity if target_entity else prompt
        
        return InputAnalysisSpec(
            category=category,
            target_entity=target_entity,
            secondary_keywords=[w for w in target_entity.split() if len(w) > 3],
            location_scope=location,
            time_period_days=30,
            url_target=url_target,
            recommended_sources=["NEWS", "REDDIT", "YOUTUBE"],
            source_queries=SourceQuerySpec(
                reddit_query=query_term,
                youtube_query=f"{query_term} review" if category == "PRODUCT" else query_term,
                news_query=query_term
            ),
            confidence_score=0.85
        )

input_analyzer = InputAnalyzerService()
