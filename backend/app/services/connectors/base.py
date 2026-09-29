from abc import ABC, abstractmethod
from typing import List, Optional
from app.schemas.source import NormalizedRecord

class BaseSourceConnector(ABC):
    """Abstract Base Class for all opinion intelligence data sources."""
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """Returns uppercase platform identifier, e.g., 'REDDIT', 'YOUTUBE', 'NEWS', 'FILE_UPLOAD'"""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Returns True if the required credentials/settings are present."""
        pass

    @abstractmethod
    async def collect(
        self,
        query: str,
        limit: int = 50,
        time_days: int = 30,
        url: Optional[str] = None
    ) -> List[NormalizedRecord]:
        """Collects and normalizes records for the given search query or direct URL."""
        pass
