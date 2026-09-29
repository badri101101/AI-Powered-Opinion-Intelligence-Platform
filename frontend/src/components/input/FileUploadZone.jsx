import React, { useRef, useState } from 'react';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, X } from 'lucide-react';
import { Button } from '../common/Button';

export const FileUploadZone = ({ onUploadFile, isUploading }) => {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [promptNote, setPromptNote] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateAndSetFile = (file) => {
    setErrorMsg('');
    if (!file) return;

    const name = file.name.toLowerCase();
    if (!name.endsWith('.csv') && !name.endsWith('.xlsx') && !name.endsWith('.xls')) {
      setErrorMsg('Invalid format. Please select a .csv or .xlsx file.');
      return;
    }

    if (file.size > 15 * 1024 * 1024) {
      setErrorMsg('File size exceeds 15MB limit.');
      return;
    }

    setSelectedFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleClear = () => {
    setSelectedFile(null);
    setPromptNote('');
    setErrorMsg('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    onUploadFile(selectedFile, promptNote);
  };

  return (
    <div className="mt-6 bg-white rounded-xl border border-slate-200 p-6 shadow-2xs">
      <div className="flex items-center gap-2 mb-3">
        <UploadCloud className="w-5 h-5 text-teal-600" />
        <h3 className="text-sm font-semibold text-slate-900">Upload Dataset (CSV / Excel)</h3>
        <span className="text-xs text-slate-500">• Analyze existing reviews or feedback survey data</span>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".csv, .xlsx, .xls"
        className="hidden"
        onChange={handleFileChange}
      />

      {!selectedFile ? (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors duration-150 ${
            dragActive ? 'border-teal-500 bg-teal-50/40' : 'border-slate-300 hover:border-slate-400 bg-slate-50/50'
          }`}
        >
          <UploadCloud className="w-8 h-8 text-slate-400 mx-auto mb-2" />
          <p className="text-sm font-medium text-slate-700">
            Click to upload or drag and drop a dataset
          </p>
          <p className="text-xs text-slate-500 mt-1">
            Supports CSV, XLSX up to 15MB (Auto-detects review, comment, and text columns)
          </p>
        </div>
      ) : (
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded bg-teal-100 flex items-center justify-center text-teal-700">
                <FileText className="w-5 h-5" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-900">{selectedFile.name}</p>
                <p className="text-xs text-slate-500">{(selectedFile.size / 1024).toFixed(1)} KB • Ready for analysis</p>
              </div>
            </div>
            <button
              type="button"
              onClick={handleClear}
              className="text-slate-400 hover:text-slate-600 p-1 cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="mt-3">
            <input
              type="text"
              placeholder="Optional: Enter context or question about this dataset (e.g. 'Analyze product satisfaction')"
              value={promptNote}
              onChange={(e) => setPromptNote(e.target.value)}
              className="w-full text-xs px-3 py-2 bg-white rounded border border-slate-200 focus:outline-none focus:ring-1 focus:ring-teal-500"
            />
          </div>

          <div className="mt-3 flex justify-end">
            <Button
              variant="teal"
              size="sm"
              onClick={handleSubmit}
              loading={isUploading}
            >
              Start Dataset Analysis
            </Button>
          </div>
        </div>
      )}

      {errorMsg && (
        <div className="mt-2.5 flex items-center gap-1.5 text-xs text-rose-600">
          <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}
    </div>
  );
};
