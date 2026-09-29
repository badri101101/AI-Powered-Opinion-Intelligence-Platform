import React from 'react';
import { Smartphone, Landmark, Sparkles, Link, Database } from 'lucide-react';

const SAMPLE_PROMPTS = [
  {
    icon: Smartphone,
    category: 'PRODUCT',
    title: 'Samsung Galaxy S26',
    prompt: 'Analyze Samsung Galaxy S26 reviews and user opinions',
  },
  {
    icon: Landmark,
    category: 'POLICY',
    title: 'EV Subsidy Policy in India',
    prompt: 'Analyze public opinion about the new EV policy in India',
  },
  {
    icon: Sparkles,
    category: 'TOPIC',
    title: 'Electric Vehicles Market',
    prompt: 'Analyze public discussions about electric vehicles charging and range',
  },
  {
    icon: Link,
    category: 'URL',
    title: 'Reddit Discussion URL',
    prompt: 'https://reddit.com/r/technology/comments/samsung_galaxy_review',
  }
];

export const ExamplePrompts = ({ onSelectPrompt }) => {
  return (
    <div className="mt-4">
      <div className="flex items-center gap-2 mb-2.5">
        <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Or try sample research prompts:
        </span>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
        {SAMPLE_PROMPTS.map((item, idx) => {
          const Icon = item.icon;
          return (
            <button
              key={idx}
              type="button"
              onClick={() => onSelectPrompt(item.prompt)}
              className="text-left p-3 rounded-lg border border-slate-200 bg-white hover:border-teal-500 hover:bg-teal-50/30 transition-all duration-150 group cursor-pointer shadow-2xs"
            >
              <div className="flex items-center gap-2 mb-1">
                <Icon className="w-4 h-4 text-slate-400 group-hover:text-teal-600 transition-colors" />
                <span className="text-xs font-semibold text-slate-900 group-hover:text-teal-900">
                  {item.title}
                </span>
              </div>
              <p className="text-[11px] text-slate-500 line-clamp-1">
                "{item.prompt}"
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
};
