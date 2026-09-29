import React from 'react';
import { Calendar, Globe, Database, Download, Sparkles, RefreshCw } from 'lucide-react';
import { CategoryBadge } from '../common/Badge';
import { Button } from '../common/Button';
import { analysesApi } from '../../api/analysesApi';

export const ReportHeader = ({ reportData, onNewAnalysis }) => {
  const { id, original_prompt, category, target_entity, location_scope, created_at, records_found, report } = reportData;

  const downloadUrl = analysesApi.getPdfDownloadUrl(id);

  const formattedDate = created_at
    ? new Date(created_at).toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      })
    : new Date().toLocaleDateString();

  return (
    <div className="bg-white border-b border-slate-200 py-6 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        
        <div>
          <div className="flex items-center gap-2.5 mb-2">
            <CategoryBadge category={category} />
            <span className="text-xs text-slate-500 font-medium">
              Target Subject: <b className="text-slate-800">{target_entity || 'Global Subject'}</b>
            </span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            {report?.report_title || `Opinion Intelligence Brief: ${target_entity || original_prompt}`}
          </h1>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 mt-2.5 text-xs text-slate-500">
            <div className="flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-slate-400" />
              <span>{formattedDate}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Globe className="w-3.5 h-3.5 text-slate-400" />
              <span>Scope: {location_scope || 'Global'}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-slate-400" />
              <span><b>{records_found}</b> Collected Records</span>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2.5 flex-shrink-0">
          <Button
            variant="outline"
            size="sm"
            icon={RefreshCw}
            onClick={onNewAnalysis}
          >
            New Query
          </Button>

          <a href={downloadUrl} download target="_blank" rel="noopener noreferrer">
            <Button
              variant="primary"
              size="sm"
              icon={Download}
            >
              Export PDF Report
            </Button>
          </a>
        </div>

      </div>
    </div>
  );
};
