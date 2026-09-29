import React from 'react';
import { ShieldCheck } from 'lucide-react';

export const Footer = () => {
  return (
    <footer className="mt-auto border-t border-slate-200/80 bg-white py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-teal-600" />
          <span>Independent Multi-Source Intelligence Engine — Verified Source Attribution</span>
        </div>
        <div>
          <span>Dual Gemini AI & Statistical NLP Pipeline • No Conversational Memory</span>
        </div>
      </div>
    </footer>
  );
};
