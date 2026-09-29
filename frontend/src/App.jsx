import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/common/Header';
import { Footer } from './components/common/Footer';
import { AnalysisInputBar } from './components/input/AnalysisInputBar';
import { ExecutionStepper } from './components/progress/ExecutionStepper';
import { ReportHeader } from './components/dashboard/ReportHeader';
import { ExecutiveSummary } from './components/dashboard/ExecutiveSummary';
import { SentimentOverview } from './components/dashboard/SentimentOverview';
import { TopicGrid } from './components/dashboard/TopicGrid';
import { TrendTimeSeries } from './components/dashboard/TrendTimeSeries';
import { SourceAttribution } from './components/dashboard/SourceAttribution';
import { CaveatsDisclaimer } from './components/dashboard/CaveatsDisclaimer';
import { RecentAnalysesDrawer } from './components/history/RecentAnalysesDrawer';
import { analysesApi } from './api/analysesApi';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from './components/common/Button';

export default function App() {
  const [view, setView] = useState('INPUT'); // 'INPUT' | 'PROGRESS' | 'REPORT' | 'ERROR'
  const [currentAnalysisId, setCurrentAnalysisId] = useState(null);
  const [statusData, setStatusData] = useState(null);
  const [reportData, setReportData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [sourcesHealth, setSourcesHealth] = useState(null);

  // Poll interval ref
  const pollIntervalRef = useRef(null);

  // Fetch connectors health on mount
  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const health = await analysesApi.getSourcesHealth();
        setSourcesHealth(health);
      } catch (err) {
        console.warn('Sources health check failed:', err);
      }
    };
    fetchHealth();
  }, []);

  // Polling pipeline progress
  useEffect(() => {
    if (view !== 'PROGRESS' || !currentAnalysisId) {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
        pollIntervalRef.current = null;
      }
      return;
    }

    const checkStatus = async () => {
      try {
        const status = await analysesApi.getAnalysisStatus(currentAnalysisId);
        setStatusData(status);

        if (status.status === 'COMPLETED') {
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          // Fetch completed report
          const fullReport = await analysesApi.getAnalysisReport(currentAnalysisId);
          setReportData(fullReport);
          setView('REPORT');
        } else if (status.status === 'FAILED') {
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          setErrorMessage(status.error_message || 'The analysis pipeline encountered an error.');
        }
      } catch (err) {
        console.error('Status poll error:', err);
      }
    };

    // Run immediately once, then interval
    checkStatus();
    pollIntervalRef.current = setInterval(checkStatus, 1500);

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [view, currentAnalysisId]);

  // Start prompt-based analysis
  const handleStartAnalysis = async (prompt, categoryOverride) => {
    try {
      setIsLoading(true);
      setErrorMessage(null);
      const res = await analysesApi.createAnalysis(prompt, categoryOverride);
      const analysisId = res.id || res.analysis_id;
      setCurrentAnalysisId(analysisId);
      setStatusData({
        status: res.status,
        current_step: 'Initializing pipeline...',
        progress_percent: 10,
        records_found: 0,
      });
      setView('PROGRESS');
    } catch (err) {
      console.error('Create analysis error:', err);
      setErrorMessage(err.response?.data?.detail || 'Failed to start analysis request.');
    } finally {
      setIsLoading(false);
    }
  };

  // Start file upload analysis
  const handleUploadDataset = async (file, prompt) => {
    try {
      setIsLoading(true);
      setErrorMessage(null);
      const res = await analysesApi.uploadDataset(file, prompt);
      const analysisId = res.id || res.analysis_id;
      setCurrentAnalysisId(analysisId);
      setStatusData({
        status: res.status,
        current_step: 'Parsing uploaded dataset...',
        progress_percent: 15,
        records_found: 0,
      });
      setView('PROGRESS');
    } catch (err) {
      console.error('Upload error:', err);
      setErrorMessage(err.response?.data?.detail || 'Failed to upload and analyze dataset.');
    } finally {
      setIsLoading(false);
    }
  };

  // Select a historical report from drawer
  const handleSelectPastAnalysis = async (analysisId) => {
    try {
      setIsLoading(true);
      setErrorMessage(null);
      setCurrentAnalysisId(analysisId);
      
      const report = await analysesApi.getAnalysisReport(analysisId);
      if (report.status === 'COMPLETED' && report.report) {
        setReportData(report);
        setView('REPORT');
      } else {
        setStatusData({
          status: report.status,
          current_step: 'Resuming analysis monitoring...',
          progress_percent: 50,
          records_found: report.records_found || 0,
        });
        setView('PROGRESS');
      }
    } catch (err) {
      console.error('Fetch past analysis error:', err);
      setErrorMessage(err.response?.data?.detail || 'Unable to open selected analysis.');
    } finally {
      setIsLoading(false);
    }
  };

  // Reset to clean Home view
  const handleReset = () => {
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
      pollIntervalRef.current = null;
    }
    setCurrentAnalysisId(null);
    setStatusData(null);
    setReportData(null);
    setErrorMessage(null);
    setView('INPUT');
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 font-sans antialiased">
      {/* Global Top Navbar */}
      <Header
        onNewAnalysis={handleReset}
        onToggleHistory={() => setIsHistoryOpen(true)}
        sourcesHealth={sourcesHealth}
      />

      {/* Global Error Banner if not in Stepper */}
      {errorMessage && view === 'INPUT' && (
        <div className="max-w-4xl mx-auto mt-6 px-4 w-full">
          <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center justify-between">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-600 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setErrorMessage(null)}
              className="font-bold hover:text-rose-950 ml-4 cursor-pointer"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      {/* Main Content Area */}
      <main className="flex-1">
        {/* VIEW 1: Input / Search Landing Page */}
        {view === 'INPUT' && (
          <AnalysisInputBar
            onStartAnalysis={handleStartAnalysis}
            onUploadDataset={handleUploadDataset}
            isLoading={isLoading}
          />
        )}

        {/* VIEW 2: Real-time Execution Stepper */}
        {view === 'PROGRESS' && (
          <ExecutionStepper
            statusData={statusData}
            onCancelOrReset={handleReset}
          />
        )}

        {/* VIEW 3: Full Opinion Intelligence Dashboard Report */}
        {view === 'REPORT' && reportData && (
          <div className="animate-fadeIn">
            {/* Report Header with PDF Export Button */}
            <ReportHeader
              reportData={reportData}
              onNewAnalysis={handleReset}
            />

            {/* Report Dashboard Main Container */}
            <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
              
              {/* 1. Executive Summary & Takeaway Findings */}
              <ExecutiveSummary
                report={reportData.report}
                metrics={reportData.metrics}
              />

              {/* 2. Sentiment Metrics & Emotion Distribution */}
              <SentimentOverview
                metrics={reportData.metrics}
              />

              {/* 3. Major Thematic Clusters (NMF / TF-IDF) */}
              <TopicGrid
                metrics={reportData.metrics}
                report={reportData.report}
              />

              {/* 4. Temporal Trends & Statistical Forecast */}
              <TrendTimeSeries
                metrics={reportData.metrics}
                report={reportData.report}
              />

              {/* 5. Source Ingestion Audit & Attribution */}
              <SourceAttribution
                sources={reportData.sources}
                recordsFound={reportData.records_found}
              />

              {/* 6. Caveats & Transparency Disclaimers */}
              <CaveatsDisclaimer
                caveats={reportData.report?.caveats_and_disclaimers}
              />

            </div>
          </div>
        )}
      </main>

      {/* Global Footer */}
      <Footer />

      {/* Recent Runs History Drawer */}
      <RecentAnalysesDrawer
        isOpen={isHistoryOpen}
        onClose={() => setIsHistoryOpen(false)}
        onSelectAnalysis={handleSelectPastAnalysis}
        currentAnalysisId={currentAnalysisId}
      />
    </div>
  );
}
