import React from 'react';
import { Info, ShieldAlert } from 'lucide-react';

export const CaveatsDisclaimer = ({ caveats }) => {
  if (!caveats) return null;

  return (
    <div className="bg-slate-50 border border-slate-200 rounded-xl p-5 text-xs text-slate-600 space-y-2">
      <div className="flex items-center gap-2 text-slate-800 font-semibold">
        <Info className="w-4 h-4 text-slate-500" />
        <span>Methodology & Platform Transparency Notice</span>
      </div>
      <p className="leading-relaxed text-slate-600">
        {caveats}
      </p>
      <div className="text-[11px] text-slate-400 pt-2 border-t border-slate-200/60">
        This automated intelligence brief aggregates public online opinions. Findings represent statistical sentiment distributions and NLP topic clusters derived from ingested public commentary without editorial bias.
      </div>
    </div>
  );
};
