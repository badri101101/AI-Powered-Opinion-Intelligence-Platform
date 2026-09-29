import React from 'react';
import { CheckCircle2, Circle, Loader2, AlertTriangle, Database, Sparkles, LineChart, FileText } from 'lucide-react';
import { Card } from '../common/Card';
import { Button } from '../common/Button';

const PIPELINE_STAGES = [
  { id: 'CLASSIFYING', label: 'Intent & Scope Classification', icon: Sparkles, desc: 'Gemini AI #1 analyzing request requirements and source queries' },
  { id: 'COLLECTING', label: 'Multi-Source Data Ingestion', icon: Database, desc: 'Harvesting discussions across News, Reddit, and YouTube' },
  { id: 'ANALYZING', label: 'Statistical NLP & Trend Engine', icon: LineChart, desc: 'Computing sentiment distribution, topic clustering & time-series' },
  { id: 'GENERATING', label: 'Evidence Synthesis & PDF Generation', icon: FileText, desc: 'Gemini AI #2 compiling report & ReportLab PDF builder' },
];

export const ExecutionStepper = ({ statusData, onCancelOrReset }) => {
  const { status, current_step, progress_percent, records_found, error_message } = statusData || {};

  const getStageState = (stageId, index) => {
    const stageOrder = ['PENDING', 'CLASSIFYING', 'COLLECTING', 'ANALYZING', 'GENERATING', 'COMPLETED'];
    const currentIndex = stageOrder.indexOf(status);
    const thisIndex = stageOrder.indexOf(stageId);

    if (status === 'FAILED') {
      return thisIndex === currentIndex ? 'error' : (thisIndex < currentIndex ? 'completed' : 'pending');
    }
    if (status === 'COMPLETED' || thisIndex < currentIndex) {
      return 'completed';
    }
    if (thisIndex === currentIndex) {
      return 'active';
    }
    return 'pending';
  };

  return (
    <div className="max-w-3xl mx-auto py-12 px-4">
      <Card className="border-slate-300 shadow-sm">
        
        {/* Progress Header */}
        <div className="flex items-center justify-between pb-6 border-b border-slate-100">
          <div>
            <div className="flex items-center gap-2">
              <Loader2 className="w-5 h-5 text-teal-600 animate-spin" />
              <h2 className="text-lg font-bold text-slate-900">Analysis In Progress</h2>
            </div>
            <p className="text-xs text-slate-500 mt-1">
              {current_step || 'Initializing intelligence pipeline...'}
            </p>
          </div>

          <div className="text-right">
            <span className="text-xl font-extrabold text-slate-900">{progress_percent || 10}%</span>
            <p className="text-[11px] text-slate-500">{records_found > 0 ? `${records_found} records collected` : 'Orchestrating'}</p>
          </div>
        </div>

        {/* Live Progress Bar */}
        <div className="w-full bg-slate-100 rounded-full h-2 mt-6 overflow-hidden">
          <div
            className="bg-slate-900 h-2 rounded-full transition-all duration-300 ease-out"
            style={{ width: `${progress_percent || 10}%` }}
          />
        </div>

        {/* Stepper Steps */}
        <div className="mt-8 space-y-4">
          {PIPELINE_STAGES.map((stage, idx) => {
            const state = getStageState(stage.id, idx);
            const Icon = stage.icon;

            return (
              <div
                key={stage.id}
                className={`flex items-start gap-4 p-3.5 rounded-xl border transition-all ${
                  state === 'active'
                    ? 'border-teal-400 bg-teal-50/40 shadow-xs'
                    : state === 'completed'
                    ? 'border-slate-200 bg-slate-50/50'
                    : state === 'error'
                    ? 'border-rose-300 bg-rose-50/50'
                    : 'border-transparent text-slate-400'
                }`}
              >
                <div className="mt-0.5 flex-shrink-0">
                  {state === 'completed' && <CheckCircle2 className="w-5 h-5 text-emerald-600" />}
                  {state === 'active' && <Loader2 className="w-5 h-5 text-teal-600 animate-spin" />}
                  {state === 'error' && <AlertTriangle className="w-5 h-5 text-rose-600" />}
                  {state === 'pending' && <Circle className="w-5 h-5 text-slate-300" />}
                </div>

                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-semibold ${state === 'active' ? 'text-slate-900' : (state === 'completed' ? 'text-slate-800' : 'text-slate-500')}`}>
                      {stage.label}
                    </span>
                    {state === 'active' && (
                      <span className="text-[10px] font-medium px-2 py-0.5 rounded-full bg-teal-100 text-teal-800">
                        Running
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-500 mt-0.5">{stage.desc}</p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Error State */}
        {error_message && (
          <div className="mt-6 p-4 rounded-lg bg-rose-50 border border-rose-200 text-rose-800 text-xs">
            <p className="font-semibold flex items-center gap-1.5 mb-1">
              <AlertTriangle className="w-4 h-4 text-rose-600" />
              Analysis Execution Failed
            </p>
            <p>{error_message}</p>
            <div className="mt-3">
              <Button variant="outline" size="sm" onClick={onCancelOrReset}>
                Try Another Analysis
              </Button>
            </div>
          </div>
        )}

      </Card>
    </div>
  );
};
