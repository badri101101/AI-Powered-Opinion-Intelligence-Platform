import React from 'react';
import { Card } from '../common/Card';
import { SourceBadge } from '../common/Badge';
import { Database, ExternalLink, CheckCircle2, AlertCircle } from 'lucide-react';

export const SourceAttribution = ({ sources = [], recordsFound = 0 }) => {
  if (sources.length === 0) return null;

  return (
    <Card
      title="Source Attribution & Ingestion Audit"
      subtitle={`Comprehensive metadata across ${sources.length} active data connectors (${recordsFound} verified items).`}
    >
      <div className="overflow-x-auto -mx-6 -mb-6">
        <table className="w-full text-left text-xs text-slate-600">
          <thead className="bg-slate-50 text-slate-700 font-semibold border-y border-slate-200 uppercase tracking-wider text-[10px]">
            <tr>
              <th className="py-3 px-6">Connector Platform</th>
              <th className="py-3 px-4">Query / Target Spec</th>
              <th className="py-3 px-4">Records Gathered</th>
              <th className="py-3 px-4">Collection Status</th>
              <th className="py-3 px-6">Ingestion Timestamp</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {sources.map((src, idx) => {
              const isSuccess = src.status === 'COMPLETED' || src.status === 'ACTIVE' || (src.records_count || 0) > 0;
              const formattedDate = src.collected_at
                ? new Date(src.collected_at).toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })
                : 'Recent';

              return (
                <tr key={idx} className="hover:bg-slate-50/70 transition-colors">
                  <td className="py-3.5 px-6 font-medium text-slate-900">
                    <div className="flex items-center gap-2">
                      <SourceBadge platform={src.platform} />
                    </div>
                  </td>

                  <td className="py-3.5 px-4 font-mono text-slate-700 max-w-xs truncate">
                    {src.query_executed || src.source_url || 'Target Entity Match'}
                  </td>

                  <td className="py-3.5 px-4 font-bold text-slate-900">
                    {src.records_count || 0}
                  </td>

                  <td className="py-3.5 px-4">
                    {isSuccess ? (
                      <span className="inline-flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full font-medium text-[11px]">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" /> Ingested
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full font-medium text-[11px]">
                        <AlertCircle className="w-3 h-3 text-amber-600" /> Empty / Skipped
                      </span>
                    )}
                  </td>

                  <td className="py-3.5 px-6 text-slate-400">
                    {formattedDate}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </Card>
  );
};
