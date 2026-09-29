import os
import json
import logging
from typing import Type, TypeVar, Optional
from pydantic import BaseModel
from google import genai
from google.genai import types
from app.config import settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if self.api_key and self.api_key.strip():
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize Gemini Client: {e}")
                self.client = None

    def is_available(self) -> bool:
        return bool(self.client and self.api_key and len(self.api_key.strip()) > 5)

    def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        schema: Type[T],
        model: Optional[str] = None
    ) -> Optional[T]:
        """Generates structured Pydantic object using Gemini with strict schema enforcement."""
        if not self.is_available():
            logger.warning("Gemini API key is not configured or client unavailable.")
            return None

        model_name = model or settings.GEMINI_ANALYZER_MODEL
        try:
            response = self.client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=schema,
                    temperature=0.2,
                ),
            )
            
            if response and response.text:
                parsed_json = json.loads(response.text)
                return schema.model_validate(parsed_json)
        except Exception as e:
            logger.error(f"Error during Gemini structured generation with {model_name}: {e}")
            return None

gemini_service = GeminiService()
