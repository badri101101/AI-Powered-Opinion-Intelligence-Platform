import React, { useState } from 'react';
import { Search, ArrowRight, Sparkles, SlidersHorizontal } from 'lucide-react';
import { Button } from '../common/Button';
import { ExamplePrompts } from './ExamplePrompts';
import { FileUploadZone } from './FileUploadZone';

export const AnalysisInputBar = ({ onStartAnalysis, onUploadDataset, isLoading }) => {
  const [prompt, setPrompt] = useState('');
  const [categoryOverride, setCategoryOverride] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!prompt.trim()) return;
    onStartAnalysis(prompt.trim(), categoryOverride || null);
  };

  const handleSelectExample = (examplePrompt) => {
    setPrompt(examplePrompt);
  };

  return (
    <div className="max-w-4xl mx-auto py-10 px-4 sm:px-6">
      
      {/* Title & Introduction */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-100 text-slate-700 text-xs font-medium border border-slate-200 mb-3">
          <Sparkles className="w-3.5 h-3.5 text-teal-600" />
          <span>Autonomous Multi-Source Opinion Intelligence</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
          What opinion landscape do you want to analyze?
        </h1>
        <p className="text-sm sm:text-base text-slate-500 mt-2 max-w-2xl mx-auto">
          Enter a product, public policy, broad industry topic, Reddit URL, or upload a dataset. The system autonomously collects multi-source data, extracts statistical insights, and compiles an evidence-grounded report.
        </p>
      </div>

      {/* Main Search Input Form */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="bg-white rounded-2xl border-2 border-slate-300 focus-within:border-slate-900 shadow-sm transition-all duration-150 p-2 sm:p-2.5 flex flex-col sm:flex-row items-center gap-2">
          
          <div className="flex items-center flex-1 w-full pl-3">
            <Search className="w-5 h-5 text-slate-400 mr-3 flex-shrink-0" />
            <input
              type="text"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="e.g. 'Analyze Samsung Galaxy S26 reviews' or 'Analyze EV policy in India'..."
              className="w-full text-slate-900 placeholder:text-slate-400 text-sm sm:text-base bg-transparent border-none focus:outline-none focus:ring-0 py-2"
              disabled={isLoading}
              autoFocus
            />
          </div>

          <div className="flex items-center justify-between w-full sm:w-auto gap-2">
            <button
              type="button"
              onClick={() => setShowFilters(!showFilters)}
              className="px-2.5 py-2 text-xs font-medium text-slate-500 hover:text-slate-800 rounded-lg hover:bg-slate-100 flex items-center gap-1.5 transition-colors cursor-pointer"
              title="Category Options"
            >
              <SlidersHorizontal className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Category</span>
            </button>

            <Button
              type="submit"
              variant="primary"
              size="md"
              loading={isLoading}
              disabled={!prompt.trim()}
              className="w-full sm:w-auto px-6"
            >
              <span>Analyze</span>
              <ArrowRight className="w-4 h-4" />
            </Button>
          </div>
        </div>

        {/* Optional Category Override Selector */}
        {showFilters && (
          <div className="mt-2.5 p-3.5 bg-white rounded-xl border border-slate-200 shadow-xs flex flex-wrap items-center gap-2 text-xs">
            <span className="font-semibold text-slate-600 mr-2">Category Classification:</span>
            {[
              { label: 'Auto-Detect Intent (AI)', value: '' },
              { label: 'Product Review', value: 'PRODUCT' },
              { label: 'Public Policy', value: 'POLICY' },
              { label: 'General Topic', value: 'TOPIC' },
              { label: 'Direct URL', value: 'URL' },
            ].map((opt) => (
              <button
                key={opt.value}
                type="button"
                onClick={() => setCategoryOverride(opt.value)}
                className={`px-3 py-1.5 rounded-lg border font-medium transition-colors cursor-pointer ${
                  categoryOverride === opt.value
                    ? 'bg-slate-900 text-white border-slate-900'
                    : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>
        )}
      </form>

      {/* Sample Queries */}
      <ExamplePrompts onSelectPrompt={handleSelectExample} />

      {/* Dataset File Upload */}
      <FileUploadZone onUploadFile={onUploadDataset} isUploading={isLoading} />

    </div>
  );
};
