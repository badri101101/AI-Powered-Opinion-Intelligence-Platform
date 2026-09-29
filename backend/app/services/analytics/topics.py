import logging
from typing import List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
from app.schemas.metrics import TopicClusterItem
from app.schemas.source import NormalizedRecord

logger = logging.getLogger(__name__)

class TopicModelingEngine:
    def extract_topics(
        self,
        records: List[NormalizedRecord],
        sentiment_scores: List[float],
        num_topics: int = 4
    ) -> List[TopicClusterItem]:
        """Discovers thematic clusters and top keywords using TF-IDF and NMF."""
        if not records:
            return []

        texts = [r.cleaned_text or r.raw_text for r in records]
        
        # If very few records, fall back to simple frequency keyword clustering
        if len(texts) < 4:
            return self._simple_keyword_topics(texts, sentiment_scores)

        try:
            vectorizer = TfidfVectorizer(
                max_df=0.85,
                min_df=2 if len(texts) > 10 else 1,
                stop_words="english",
                ngram_range=(1, 2),
                max_features=200
            )
            tfidf_matrix = vectorizer.fit_transform(texts)
            feature_names = np.array(vectorizer.get_feature_names_out())

            k = min(num_topics, max(2, len(texts) // 4))
            nmf = NMF(n_components=k, random_state=42, max_iter=200)
            doc_topic_matrix = nmf.fit_transform(tfidf_matrix)

            assigned_topics = doc_topic_matrix.argmax(axis=1)

            topic_clusters: List[TopicClusterItem] = []
            total_docs = len(texts)

            for topic_idx in range(k):
                # Top keyword indices for this topic
                top_word_indices = nmf.components_[topic_idx].argsort()[::-1][:5]
                keywords = [str(feature_names[i]) for i in top_word_indices if i < len(feature_names)]
                
                # Documents assigned to this topic
                doc_indices = np.where(assigned_topics == topic_idx)[0]
                doc_count = len(doc_indices)
                
                if doc_count == 0 and len(keywords) == 0:
                    continue

                topic_sentiments = [sentiment_scores[i] for i in doc_indices if i < len(sentiment_scores)]
                avg_sent = float(np.mean(topic_sentiments)) if topic_sentiments else 0.0

                # Formulate a natural cluster name from top keywords
                topic_title = " & ".join([w.title() for w in keywords[:2]]) if keywords else f"Topic {topic_idx + 1}"

                topic_clusters.append(TopicClusterItem(
                    topic_id=topic_idx + 1,
                    name=topic_title,
                    keywords=keywords,
                    count=doc_count,
                    share_percentage=round((doc_count / total_docs) * 100, 1) if total_docs > 0 else 0.0,
                    sentiment_score=round(avg_sent, 2)
                ))

            # Sort by volume share descending
            topic_clusters.sort(key=lambda x: x.count, reverse=True)
            return topic_clusters

        except Exception as e:
            logger.warning(f"Error in NMF topic modeling: {e}. Falling back to simple keyword extraction.")
            return self._simple_keyword_topics(texts, sentiment_scores)

    def _simple_keyword_topics(self, texts: List[str], sentiment_scores: List[float]) -> List[TopicClusterItem]:
        """Lightweight fallback topic extractor for small datasets."""
        try:
            vectorizer = TfidfVectorizer(stop_words="english", max_features=15)
            X = vectorizer.fit_transform(texts)
            words = vectorizer.get_feature_names_out()
            
            avg_score = float(np.mean(sentiment_scores)) if sentiment_scores else 0.0
            return [TopicClusterItem(
                topic_id=1,
                name="Key Themes & Highlights",
                keywords=list(words[:5]),
                count=len(texts),
                share_percentage=100.0,
                sentiment_score=round(avg_score, 2)
            )]
        except Exception:
            return []

topic_engine = TopicModelingEngine()
