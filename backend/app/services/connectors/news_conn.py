import re
import urllib.parse
import logging
from datetime import datetime, timezone
from typing import List, Optional
import feedparser
from app.services.connectors.base import BaseSourceConnector
from app.schemas.source import NormalizedRecord

logger = logging.getLogger(__name__)

class NewsRSSConnector(BaseSourceConnector):
    @property
    def platform_name(self) -> str:
        return "NEWS"

    def is_configured(self) -> bool:
        # Public RSS feeds do not require external credentials
        return True

    async def collect(
        self,
        query: str,
        limit: int = 50,
        time_days: int = 30,
        url: Optional[str] = None
    ) -> List[NormalizedRecord]:
        records: List[NormalizedRecord] = []
        try:
            target_url = url
            if not target_url:
                encoded_query = urllib.parse.quote(query)
                target_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"

            feed = feedparser.parse(target_url)
            
            for entry in feed.entries[:limit]:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                # Clean HTML tags
                clean_summary = re.sub(r'<[^>]+>', '', summary).strip()
                full_text = f"{title}. {clean_summary}".strip()
                if not full_text:
                    continue

                # Parse published datetime
                published_at = None
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    except Exception:
                        published_at = datetime.now(timezone.utc)
                else:
                    published_at = datetime.now(timezone.utc)

                source_name = "News Feed"
                if hasattr(entry, "source") and entry.source and hasattr(entry.source, "title"):
                    source_name = entry.source.title

                records.append(NormalizedRecord(
                    platform=self.platform_name,
                    external_id=entry.get("id", entry.get("link")),
                    raw_text=full_text,
                    author=source_name,
                    published_at=published_at,
                    engagement_score=10,
                    source_url=entry.get("link", target_url),
                    metadata={"publisher": source_name, "guid": entry.get("id")}
                ))
            
            logger.info(f"News connector harvested {len(records)} records for query '{query}'.")
        except Exception as e:
            logger.error(f"Error fetching news RSS feed for query '{query}': {e}")

        return records

news_connector = NewsRSSConnector()
