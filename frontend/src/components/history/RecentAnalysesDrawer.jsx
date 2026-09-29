import React, { useState, useEffect } from 'react';
import { X, Clock, ArrowRight, Layers, AlertCircle, RefreshCw } from 'lucide-react';
import { CategoryBadge, StatusBadge } from '../common/Badge';
import { analysesApi } from '../../api/analysesApi';

export const RecentAnalysesDrawer = ({ isOpen, onClose, onSelectAnalysis, currentAnalysisId }) => {
  const [analyses, setAnalyses] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecent = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await analysesApi.listRecentAnalyses(20);
      setAnalyses(data || []);
    } catch (err) {
      setError('Unable to load past analyses history.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchRecent();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-slate-900/40 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white shadow-2xl border-l border-slate-200 flex flex-col">
          
          {/* Drawer Header */}
          <div className="p-5 border-b border-slate-200 flex items-center justify-between bg-slate-50">
            <div className="flex items-center gap-2">
              <Clock className="w-5 h-5 text-indigo-600" />
              <h2 className="text-base font-bold text-slate-900">Analysis History</h2>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={fetchRecent}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-md hover:bg-slate-200/60"
                title="Refresh"
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </button>
              <button
                onClick={onClose}
                className="p-1.5 text-slate-400 hover:text-slate-600 rounded-md hover:bg-slate-200/60"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* List Content */}
          <div className="flex-1 overflow-y-auto p-4 divide-y divide-slate-100">
            {loading ? (
              <div className="py-12 text-center text-xs text-slate-400">
                <RefreshCw className="w-5 h-5 animate-spin mx-auto mb-2 text-indigo-600" />
                Loading past runs...
              </div>
            ) : error ? (
              <div className="py-12 text-center text-xs text-rose-500">
                <AlertCircle className="w-5 h-5 mx-auto mb-2" />
                {error}
              </div>
            ) : analyses.length === 0 ? (
              <div className="py-12 text-center text-xs text-slate-400">
                No past analysis runs found in database.
              </div>
            ) : (
              analyses.map((item) => {
                const isSelected = item.id === currentAnalysisId;
                const formattedDate = item.created_at
                  ? new Date(item.created_at).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })
                  : '';

                return (
                  <div
                    key={item.id}
                    onClick={() => {
                      onSelectAnalysis(item.id);
                      onClose();
                    }}
                    className={`py-3.5 px-3 rounded-lg cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-indigo-50/70 border border-indigo-200'
                        : 'hover:bg-slate-50'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1.5">
                      <CategoryBadge category={item.category} />
                      <StatusBadge status={item.status} />
                    </div>

                    <p className="text-xs font-semibold text-slate-900 leading-snug line-clamp-2 mb-1">
                      {item.original_prompt}
                    </p>

                    <div className="flex items-center justify-between text-[11px] text-slate-400 mt-2">
                      <span>{formattedDate}</span>
                      <span className="flex items-center gap-1 text-indigo-600 font-medium group-hover:translate-x-0.5 transition-transform">
                        Open Report <ArrowRight className="w-3 h-3" />
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>

          {/* Drawer Footer */}
          <div className="p-4 border-t border-slate-200 bg-slate-50 text-[11px] text-slate-500 text-center">
            Every analysis is persisted independently with full audit metrics.
          </div>

        </div>
      </div>
    </div>
  );
};
