import React from 'react';
import { Card } from '../common/Card';
import { Layers, Tag, TrendingUp, TrendingDown } from 'lucide-react';

export const TopicGrid = ({ metrics, report }) => {
  const topicClusters = metrics?.topic_clusters || [];
  const topicSummaries = report?.topic_summaries || [];

  if (topicClusters.length === 0 && topicSummaries.length === 0) return null;

  // Merge cluster statistics with topic narrative summaries by index/name
  const mergedTopics = topicClusters.map((cluster, idx) => {
    const summaryMatch = topicSummaries.find(
      (s) => s.topic_name?.toLowerCase() === cluster.name?.toLowerCase()
    ) || topicSummaries[idx];

    return {
      id: cluster.topic_id ?? idx + 1,
      name: cluster.name,
      keywords: cluster.keywords || [],
      count: cluster.count || 0,
      share_percentage: cluster.share_percentage || 0,
      sentiment_score: cluster.sentiment_score || 0,
      summary: summaryMatch?.summary || '',
      sentiment_note: summaryMatch?.sentiment_note || '',
    };
  });

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
            <Layers className="w-5 h-5 text-indigo-600" />
            <span>Major Thematic Clusters</span>
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Key topics extracted via TF-IDF and Non-Negative Matrix Factorization (NMF) clustering.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {mergedTopics.map((topic) => (
          <div
            key={topic.id}
            className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs hover:border-slate-300 transition-all flex flex-col justify-between"
          >
            <div>
              {/* Card Header: Topic Name & Share */}
              <div className="flex items-start justify-between gap-3 mb-2.5">
                <div>
                  <span className="text-[10px] font-bold text-indigo-600 uppercase tracking-wider block mb-0.5">
                    Cluster #{topic.id}
                  </span>
                  <h3 className="font-semibold text-slate-900 text-sm leading-tight capitalize">
                    {topic.name}
                  </h3>
                </div>
                <div className="text-right flex-shrink-0">
                  <span className="text-sm font-bold text-slate-800">
                    {topic.share_percentage}%
                  </span>
                  <span className="text-[10px] text-slate-400 block font-mono">
                    {topic.count} items
                  </span>
                </div>
              </div>

              {/* Topic Synthesis Narrative */}
              {topic.summary ? (
                <p className="text-xs text-slate-600 leading-relaxed mb-3 bg-slate-50 p-2.5 rounded-lg border border-slate-100">
                  {topic.summary}
                </p>
              ) : null}

              {/* Keywords Tag Chips */}
              {topic.keywords.length > 0 && (
                <div className="flex flex-wrap gap-1.5 mb-4">
                  {topic.keywords.map((kw, kwIdx) => (
                    <span
                      key={kwIdx}
                      className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 text-[11px] font-medium"
                    >
                      <Tag className="w-2.5 h-2.5 text-slate-400" />
                      {kw}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Card Footer: Sentiment slant and score */}
            <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-xs">
              <span className="text-slate-500 font-medium">Topic Polarity:</span>
              <div className="flex items-center gap-1.5 font-bold">
                {topic.sentiment_score > 0.05 ? (
                  <span className="text-emerald-600 flex items-center gap-1">
                    <TrendingUp className="w-3.5 h-3.5" />
                    +{topic.sentiment_score.toFixed(2)}
                  </span>
                ) : topic.sentiment_score < -0.05 ? (
                  <span className="text-rose-600 flex items-center gap-1">
                    <TrendingDown className="w-3.5 h-3.5" />
                    {topic.sentiment_score.toFixed(2)}
                  </span>
                ) : (
                  <span className="text-slate-500">
                    {topic.sentiment_score.toFixed(2)}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
