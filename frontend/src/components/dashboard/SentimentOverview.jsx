import React from 'react';
import { Card } from '../common/Card';
import { SentimentBadge } from '../common/Badge';
import { Smile, Frown, Meh, HeartHandshake, ShieldCheck, Flame, Zap, Compass } from 'lucide-react';

export const SentimentOverview = ({ metrics }) => {
  if (!metrics) return null;

  const {
    sentiment_distribution = {
      positive: 0,
      neutral: 0,
      negative: 0,
      average_compound_score: 0,
      label: 'Neutral',
    },
    emotion_scores = {
      joy: 0,
      trust: 0,
      surprise: 0,
      sadness: 0,
      anger: 0,
    },
    entity_mentions = [],
    total_records_analyzed = 0,
  } = metrics;

  const { positive, neutral, negative, average_compound_score, label } = sentiment_distribution;

  const emotionList = [
    { label: 'Joy / Satisfaction', score: emotion_scores.joy || 0, color: 'bg-emerald-500', icon: Smile },
    { label: 'Trust / Confidence', score: emotion_scores.trust || 0, color: 'bg-blue-500', icon: ShieldCheck },
    { label: 'Surprise / Anticipation', score: emotion_scores.surprise || 0, color: 'bg-amber-500', icon: Zap },
    { label: 'Sadness / Disappointment', score: emotion_scores.sadness || 0, color: 'bg-indigo-400', icon: Meh },
    { label: 'Anger / Frustration', score: emotion_scores.anger || 0, color: 'bg-rose-500', icon: Flame },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      {/* 1. Net Sentiment & Polarity Distribution */}
      <Card
        title="Overall Sentiment Distribution"
        subtitle={`Aggregated across ${total_records_analyzed.toLocaleString()} clean records.`}
        className="lg:col-span-2"
      >
        <div className="space-y-6">
          
          {/* Top Score Summary Banner */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-200 gap-4">
            <div>
              <span className="text-xs text-slate-500 font-medium uppercase tracking-wider block mb-1">
                Net Compound Polarity
              </span>
              <div className="flex items-baseline gap-2.5">
                <span className={`text-3xl font-extrabold ${
                  average_compound_score > 0.05 ? 'text-emerald-600' :
                  average_compound_score < -0.05 ? 'text-rose-600' : 'text-slate-700'
                }`}>
                  {average_compound_score > 0 ? `+${average_compound_score.toFixed(2)}` : average_compound_score.toFixed(2)}
                </span>
                <span className="text-xs text-slate-400 font-mono">Range: -1.0 to +1.0</span>
              </div>
            </div>

            <div className="flex sm:flex-col items-center sm:items-end gap-2">
              <span className="text-xs text-slate-500 font-medium">Consensus Slant:</span>
              <SentimentBadge label={label} score={average_compound_score} />
            </div>
          </div>

          {/* Segmented Distribution Bar */}
          <div>
            <div className="flex justify-between items-center text-xs font-semibold text-slate-700 mb-2">
              <span>Sentiment Breakdown</span>
              <span className="text-slate-400 font-normal">100% Normalized</span>
            </div>

            {/* Stacked bar */}
            <div className="w-full h-4 bg-slate-100 rounded-full overflow-hidden flex shadow-inner">
              <div
                style={{ width: `${positive}%` }}
                className="bg-emerald-500 transition-all duration-500 hover:opacity-90"
                title={`Positive: ${positive}%`}
              />
              <div
                style={{ width: `${neutral}%` }}
                className="bg-slate-300 transition-all duration-500 hover:opacity-90"
                title={`Neutral: ${neutral}%`}
              />
              <div
                style={{ width: `${negative}%` }}
                className="bg-rose-500 transition-all duration-500 hover:opacity-90"
                title={`Negative: ${negative}%`}
              />
            </div>

            {/* Legend pills */}
            <div className="grid grid-cols-3 gap-3 mt-4 text-center">
              <div className="p-2.5 rounded-lg bg-emerald-50 border border-emerald-100">
                <div className="flex items-center justify-center gap-1.5 text-xs font-medium text-emerald-800 mb-0.5">
                  <Smile className="w-3.5 h-3.5 text-emerald-600" /> Positive
                </div>
                <div className="text-lg font-bold text-emerald-700">{positive}%</div>
              </div>

              <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200">
                <div className="flex items-center justify-center gap-1.5 text-xs font-medium text-slate-700 mb-0.5">
                  <Meh className="w-3.5 h-3.5 text-slate-500" /> Neutral
                </div>
                <div className="text-lg font-bold text-slate-700">{neutral}%</div>
              </div>

              <div className="p-2.5 rounded-lg bg-rose-50 border border-rose-100">
                <div className="flex items-center justify-center gap-1.5 text-xs font-medium text-rose-800 mb-0.5">
                  <Frown className="w-3.5 h-3.5 text-rose-600" /> Negative
                </div>
                <div className="text-lg font-bold text-rose-700">{negative}%</div>
              </div>
            </div>
          </div>

          {/* Key Entity Mentions list if available */}
          {entity_mentions.length > 0 && (
            <div className="pt-2 border-t border-slate-100">
              <span className="text-xs font-semibold text-slate-700 block mb-2">
                Top Entity & Aspect Mentions
              </span>
              <div className="flex flex-wrap gap-2">
                {entity_mentions.slice(0, 8).map((ent, idx) => (
                  <div
                    key={idx}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-white border border-slate-200 text-xs font-medium text-slate-800 shadow-2xs"
                  >
                    <span>{ent.entity}</span>
                    <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-slate-100 text-slate-500 font-mono">
                      {ent.count}
                    </span>
                    <span
                      className={`text-[10px] font-bold ${
                        ent.sentiment_score > 0.05
                          ? 'text-emerald-600'
                          : ent.sentiment_score < -0.05
                          ? 'text-rose-600'
                          : 'text-slate-500'
                      }`}
                    >
                      {ent.sentiment_score > 0 ? `+${ent.sentiment_score.toFixed(2)}` : ent.sentiment_score.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>
      </Card>

      {/* 2. Emotional Intensity Breakdown */}
      <Card
        title="Emotion Breakdown"
        subtitle="Distribution of affective expressions in opinion text."
      >
        <div className="space-y-4 pt-1">
          {emotionList.map((item, idx) => {
            const Icon = item.icon;
            return (
              <div key={idx}>
                <div className="flex justify-between items-center text-xs mb-1">
                  <div className="flex items-center gap-1.5 font-medium text-slate-700">
                    <Icon className="w-3.5 h-3.5 text-slate-500" />
                    <span>{item.label}</span>
                  </div>
                  <span className="font-semibold text-slate-900">{item.score}%</span>
                </div>
                <div className="w-full h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div
                    style={{ width: `${Math.min(item.score, 100)}%` }}
                    className={`h-full ${item.color} rounded-full transition-all duration-500`}
                  />
                </div>
              </div>
            );
          })}

          <p className="text-[11px] text-slate-400 leading-normal pt-2 border-t border-slate-100">
            Scores reflect the relative density of emotion-bearing lexical markers across the corpus.
          </p>
        </div>
      </Card>

    </div>
  );
};
