import re
import logging
from datetime import datetime, timezone
from typing import List, Optional
from googleapiclient.discovery import build
from app.config import settings
from app.services.connectors.base import BaseSourceConnector
from app.schemas.source import NormalizedRecord

logger = logging.getLogger(__name__)

class YouTubeConnector(BaseSourceConnector):
    @property
    def platform_name(self) -> str:
        return "YOUTUBE"

    def is_configured(self) -> bool:
        return bool(
            settings.YOUTUBE_API_KEY and 
            len(settings.YOUTUBE_API_KEY.strip()) > 5 and
            "your_youtube" not in settings.YOUTUBE_API_KEY
        )

    def _extract_video_id(self, url: str) -> Optional[str]:
        match = re.search(r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', url)
        return match.group(1) if match else None

    async def collect(
        self,
        query: str,
        limit: int = 50,
        time_days: int = 30,
        url: Optional[str] = None
    ) -> List[NormalizedRecord]:
        records: List[NormalizedRecord] = []
        if not self.is_configured():
            logger.info("YouTube API key not configured. Skipping YouTube collection.")
            return records

        try:
            youtube = build("youtube", "v3", developerKey=settings.YOUTUBE_API_KEY)
            video_ids = []

            if url:
                vid = self._extract_video_id(url)
                if vid:
                    video_ids.append(vid)

            if not video_ids:
                # Search for top videos matching query
                search_response = youtube.search().list(
                    q=query,
                    part="snippet",
                    type="video",
                    maxResults=min(limit // 10, 5),
                    order="relevance"
                ).execute()
                
                for item in search_response.get("items", []):
                    vid = item.get("id", {}).get("videoId")
                    if vid:
                        video_ids.append(vid)
                        # Store video title & description
                        snippet = item.get("snippet", {})
                        records.append(NormalizedRecord(
                            platform=self.platform_name,
                            external_id=vid,
                            raw_text=f"{snippet.get('title', '')}. {snippet.get('description', '')}".strip(),
                            author=snippet.get("channelTitle", "YouTube Creator"),
                            published_at=datetime.fromisoformat(snippet.get("publishedAt").replace("Z", "+00:00")),
                            engagement_score=50,
                            source_url=f"https://www.youtube.com/watch?v={vid}",
                            metadata={"type": "video_snippet", "channel": snippet.get("channelTitle")}
                        ))

            # Fetch comments for identified videos
            for vid in video_ids:
                try:
                    comments_response = youtube.commentThreads().list(
                        part="snippet",
                        videoId=vid,
                        maxResults=min(limit // len(video_ids), 20),
                        textFormat="plainText"
                    ).execute()
                    
                    for item in comments_response.get("items", []):
                        top_comment = item.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                        text = top_comment.get("textDisplay", "").strip()
                        if text:
                            published_at = datetime.fromisoformat(top_comment.get("publishedAt").replace("Z", "+00:00"))
                            records.append(NormalizedRecord(
                                platform=self.platform_name,
                                external_id=item.get("id"),
                                raw_text=text,
                                author=top_comment.get("authorDisplayName", "Viewer"),
                                published_at=published_at,
                                engagement_score=top_comment.get("likeCount", 0),
                                source_url=f"https://www.youtube.com/watch?v={vid}",
                                metadata={"video_id": vid, "like_count": top_comment.get("likeCount", 0)}
                            ))
                except Exception as comment_err:
                    logger.warning(f"Could not retrieve comments for YouTube video {vid}: {comment_err}")

            logger.info(f"YouTube connector gathered {len(records)} records for query '{query}'.")
        except Exception as e:
            logger.error(f"Error executing YouTube API collection: {e}")

        return records[:limit]

youtube_connector = YouTubeConnector()
