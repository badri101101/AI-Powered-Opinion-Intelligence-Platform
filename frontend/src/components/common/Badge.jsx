import React from 'react';

export const Badge = ({ children, variant = 'default', className = '' }) => {
  const variants = {
    default: 'bg-slate-100 text-slate-700 border-slate-200',
    primary: 'bg-slate-900 text-white border-slate-900',
    success: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    warning: 'bg-amber-50 text-amber-700 border-amber-200',
    danger: 'bg-rose-50 text-rose-700 border-rose-200',
    info: 'bg-blue-50 text-blue-700 border-blue-200',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${variants[variant] || variants.default} ${className}`}
    >
      {children}
    </span>
  );
};

export const CategoryBadge = ({ category }) => {
  const styles = {
    PRODUCT: 'bg-blue-50 text-blue-700 border-blue-200',
    POLICY: 'bg-purple-50 text-purple-700 border-purple-200',
    TOPIC: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    URL: 'bg-amber-50 text-amber-700 border-amber-200',
    DATASET: 'bg-indigo-50 text-indigo-700 border-indigo-200',
  };

  const styleClass = styles[category] || 'bg-slate-100 text-slate-700 border-slate-200';

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styleClass}`}>
      {category || 'GENERAL'}
    </span>
  );
};

export const SentimentBadge = ({ label, score }) => {
  let styleClass = 'bg-slate-100 text-slate-700 border-slate-200';
  
  if (score > 0.05 || (label && label.toLowerCase().includes('positive'))) {
    styleClass = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  } else if (score < -0.05 || (label && label.toLowerCase().includes('negative'))) {
    styleClass = 'bg-rose-50 text-rose-700 border-rose-200';
  } else {
    styleClass = 'bg-amber-50 text-amber-700 border-amber-200';
  }

  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styleClass}`}>
      {label || (score > 0 ? `+${score}` : score)}
    </span>
  );
};

export const SourceBadge = ({ platform }) => {
  const styles = {
    REDDIT: 'bg-orange-50 text-orange-700 border-orange-200',
    YOUTUBE: 'bg-red-50 text-red-700 border-red-200',
    NEWS: 'bg-blue-50 text-blue-700 border-blue-200',
    FILE_UPLOAD: 'bg-teal-50 text-teal-700 border-teal-200',
  };

  const styleClass = styles[platform] || 'bg-slate-100 text-slate-700 border-slate-200';

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-bold border ${styleClass}`}>
      {platform || 'CONNECTOR'}
    </span>
  );
};

export const StatusBadge = ({ status }) => {
  const styles = {
    COMPLETED: 'bg-emerald-50 text-emerald-700 border-emerald-200',
    PENDING: 'bg-slate-100 text-slate-600 border-slate-200',
    CLASSIFYING: 'bg-blue-50 text-blue-700 border-blue-200',
    COLLECTING: 'bg-indigo-50 text-indigo-700 border-indigo-200',
    ANALYZING: 'bg-purple-50 text-purple-700 border-purple-200',
    GENERATING: 'bg-amber-50 text-amber-700 border-amber-200',
    FAILED: 'bg-rose-50 text-rose-700 border-rose-200',
  };

  const styleClass = styles[status] || 'bg-slate-100 text-slate-700 border-slate-200';

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold border uppercase tracking-wider ${styleClass}`}>
      {status || 'UNKNOWN'}
    </span>
  );
};
