import logging
from datetime import datetime, timezone
from typing import List, Optional
import praw
from app.config import settings
from app.services.connectors.base import BaseSourceConnector
from app.schemas.source import NormalizedRecord

logger = logging.getLogger(__name__)

class RedditConnector(BaseSourceConnector):
    @property
    def platform_name(self) -> str:
        return "REDDIT"

    def is_configured(self) -> bool:
        return bool(
            settings.REDDIT_CLIENT_ID and 
            settings.REDDIT_CLIENT_SECRET and 
            len(settings.REDDIT_CLIENT_ID.strip()) > 3 and
            "your_reddit" not in settings.REDDIT_CLIENT_ID
        )

    def _get_reddit_client(self) -> Optional[praw.Reddit]:
        if not self.is_configured():
            return None
        try:
            return praw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent=settings.REDDIT_USER_AGENT
            )
        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            return None

    async def collect(
        self,
        query: str,
        limit: int = 50,
        time_days: int = 30,
        url: Optional[str] = None
    ) -> List[NormalizedRecord]:
        records: List[NormalizedRecord] = []
        reddit = self._get_reddit_client()
        
        if not reddit:
            logger.info("Reddit connector not configured. Skipping Reddit API collection.")
            return records

        try:
            if url and "reddit.com" in url:
                submission = reddit.submission(url=url)
                # Add submission post
                post_text = f"{submission.title}. {submission.selftext}".strip()
                records.append(NormalizedRecord(
                    platform=self.platform_name,
                    external_id=submission.id,
                    raw_text=post_text,
                    author=str(submission.author) if submission.author else "anonymous",
                    published_at=datetime.fromtimestamp(submission.created_utc, tz=timezone.utc),
                    engagement_score=submission.score,
                    source_url=f"https://reddit.com{submission.permalink}",
                    metadata={"subreddit": str(submission.subreddit), "num_comments": submission.num_comments}
                ))
                
                # Fetch top comments
                submission.comments.replace_more(limit=0)
                for comment in submission.comments[:limit]:
                    if comment.body and comment.body != "[deleted]":
                        records.append(NormalizedRecord(
                            platform=self.platform_name,
                            external_id=comment.id,
                            raw_text=comment.body,
                            author=str(comment.author) if comment.author else "anonymous",
                            published_at=datetime.fromtimestamp(comment.created_utc, tz=timezone.utc),
                            engagement_score=comment.score,
                            source_url=f"https://reddit.com{submission.permalink}{comment.id}",
                            metadata={"parent_id": comment.parent_id, "subreddit": str(submission.subreddit)}
                        ))
            else:
                # Search across all or popular subreddits
                subreddit = reddit.subreddit("all")
                time_filter = "month" if time_days <= 30 else ("year" if time_days <= 365 else "all")
                submissions = subreddit.search(query, limit=min(limit // 2, 25), time_filter=time_filter, sort="relevance")
                
                for sub in submissions:
                    text_content = f"{sub.title}. {sub.selftext}".strip()
                    if not text_content:
                        continue
                    records.append(NormalizedRecord(
                        platform=self.platform_name,
                        external_id=sub.id,
                        raw_text=text_content,
                        author=str(sub.author) if sub.author else "anonymous",
                        published_at=datetime.fromtimestamp(sub.created_utc, tz=timezone.utc),
                        engagement_score=sub.score,
                        source_url=f"https://reddit.com{sub.permalink}",
                        metadata={"subreddit": str(sub.subreddit), "upvote_ratio": sub.upvote_ratio}
                    ))
                    
                    # Fetch top comments per submission
                    try:
                        sub.comments.replace_more(limit=0)
                        for comment in sub.comments[:5]:
                            if comment.body and comment.body != "[deleted]":
                                records.append(NormalizedRecord(
                                    platform=self.platform_name,
                                    external_id=comment.id,
                                    raw_text=comment.body,
                                    author=str(comment.author) if comment.author else "anonymous",
                                    published_at=datetime.fromtimestamp(comment.created_utc, tz=timezone.utc),
                                    engagement_score=comment.score,
                                    source_url=f"https://reddit.com{sub.permalink}{comment.id}",
                                    metadata={"subreddit": str(sub.subreddit)}
                                ))
                    except Exception:
                        pass
            
            logger.info(f"Reddit connector collected {len(records)} records for query '{query}'.")
        except Exception as e:
            logger.error(f"Error executing Reddit collection: {e}")

        return records[:limit]

reddit_connector = RedditConnector()
