import React from 'react';
import { Sparkles, Activity, History, PlusCircle } from 'lucide-react';
import { Button } from './Button';

export const Header = ({ onNewAnalysis, onToggleHistory, sourcesHealth }) => {
  return (
    <header className="bg-white border-b border-slate-200/80 sticky top-0 z-30 shadow-2xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand Logo */}
        <div className="flex items-center gap-3 cursor-pointer" onClick={onNewAnalysis}>
          <div className="w-9 h-9 rounded-lg bg-slate-900 flex items-center justify-center text-white shadow-xs">
            <Sparkles className="w-5 h-5 text-teal-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-bold text-slate-900 tracking-tight text-lg">OpinionIntel</span>
              <span className="text-[10px] font-semibold bg-teal-50 text-teal-700 px-1.5 py-0.5 rounded border border-teal-200 uppercase tracking-wider">
                Multi-Source
              </span>
            </div>
            <p className="text-[11px] text-slate-500 font-normal leading-none mt-0.5">
              AI-Powered Autonomous Opinion Intelligence
            </p>
          </div>
        </div>

        {/* Right Navigation & Status */}
        <div className="flex items-center gap-3">
          {sourcesHealth && (
            <div className="hidden md:flex items-center gap-2 text-xs text-slate-600 bg-slate-50 px-3 py-1.5 rounded-full border border-slate-200">
              <Activity className="w-3.5 h-3.5 text-teal-600" />
              <span>
                <b>{sourcesHealth.active_sources_count}</b> Connectors Ready
              </span>
            </div>
          )}

          <Button
            variant="outline"
            size="sm"
            icon={History}
            onClick={onToggleHistory}
            className="hidden sm:inline-flex"
          >
            History
          </Button>

          <Button
            variant="primary"
            size="sm"
            icon={PlusCircle}
            onClick={onNewAnalysis}
          >
            New Analysis
          </Button>
        </div>

      </div>
    </header>
  );
};
