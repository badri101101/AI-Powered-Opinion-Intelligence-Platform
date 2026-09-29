import React from 'react';
import { Card } from '../common/Card';
import { Badge } from '../common/Badge';
import { CheckCircle, AlertTriangle, HelpCircle, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

export const ExecutiveSummary = ({ report, metrics }) => {
  if (!report) return null;

  const { executive_summary, key_findings = [] } = report;

  const getImpactBadge = (impact) => {
    switch (impact?.toUpperCase()) {
      case 'POSITIVE':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <ArrowUpRight className="w-3 h-3" /> Positive Driver
          </span>
        );
      case 'NEGATIVE':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <ArrowDownRight className="w-3 h-3" /> Critical Concern
          </span>
        );
      case 'MIXED':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            <HelpCircle className="w-3 h-3" /> Mixed Sentiment
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 border border-slate-200">
            <Minus className="w-3 h-3" /> Neutral Observation
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Executive Narrative */}
      <Card
        title="Executive Summary"
        subtitle="AI synthesized narrative grounded strictly in quantified multi-source opinion data."
      >
        <div className="prose prose-slate max-w-none text-slate-700 leading-relaxed text-sm sm:text-base font-normal">
          {executive_summary.split('\n\n').map((para, i) => (
            <p key={i} className="mb-3 last:mb-0">
              {para}
            </p>
          ))}
        </div>
      </Card>

      {/* Key Findings */}
      {key_findings.length > 0 && (
        <div>
          <h2 className="text-lg font-bold text-slate-900 mb-3 flex items-center gap-2">
            <span>Key Strategic Findings</span>
            <span className="text-xs font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
              {key_findings.length} takeaways
            </span>
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {key_findings.map((finding, idx) => (
              <div
                key={idx}
                className="bg-white border border-slate-200 rounded-xl p-5 shadow-xs hover:border-slate-300 transition-colors flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2 mb-2.5">
                    <h3 className="font-semibold text-slate-900 text-sm leading-snug">
                      {finding.title}
                    </h3>
                  </div>
                  <p className="text-xs text-slate-600 leading-relaxed mb-4">
                    {finding.description}
                  </p>
                </div>

                <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                  {getImpactBadge(finding.impact)}
                  <span className="text-[11px] text-slate-400 font-mono">#{idx + 1}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
