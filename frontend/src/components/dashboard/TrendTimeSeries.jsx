import React from 'react';
import { Card } from '../common/Card';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { TrendingUp, TrendingDown, Minus, AlertCircle, Sparkles, BarChart2 } from 'lucide-react';

export const TrendTimeSeries = ({ metrics, report }) => {
  if (!metrics) return null;

  const timeSeries = metrics.time_series_trends || [];
  const forecast = metrics.forecast_data || { available: false };
  const trendNarrative = report?.trend_narrative;
  const forecastInterpretation = report?.forecast_interpretation;

  // Format data for chart
  const chartData = timeSeries.map((pt) => ({
    date: pt.date ? pt.date.slice(5) : '', // 'MM-DD'
    fullDate: pt.date,
    volume: pt.count,
    sentiment: Number(pt.sentiment_score.toFixed(2)),
  }));

  // Append projected forecast points if available
  if (forecast.available && forecast.projected_points?.length > 0) {
    forecast.projected_points.forEach((p) => {
      chartData.push({
        date: p.date ? p.date.slice(5) : '',
        fullDate: p.date,
        sentiment: null,
        projected: Number(p.projected_sentiment.toFixed(2)),
        upper: Number(p.confidence_upper.toFixed(2)),
        lower: Number(p.confidence_lower.toFixed(2)),
        isForecast: true,
      });
    });
  }

  const getTrendIcon = () => {
    switch (forecast.trend_direction?.toUpperCase()) {
      case 'UPWARD':
        return <TrendingUp className="w-5 h-5 text-emerald-600" />;
      case 'DOWNWARD':
        return <TrendingDown className="w-5 h-5 text-rose-600" />;
      default:
        return <Minus className="w-5 h-5 text-slate-500" />;
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      {/* 1. Time-Series Trajectory Chart */}
      <Card
        title="Temporal Trajectory & Momentum"
        subtitle="Chronological opinion sentiment velocity across collection timeline."
        className="lg:col-span-2"
      >
        {chartData.length > 0 ? (
          <div className="space-y-4">
            <div className="h-64 sm:h-72 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 15, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis
                    dataKey="date"
                    tick={{ fontSize: 11, fill: '#64748b' }}
                    tickLine={false}
                    axisLine={{ stroke: '#cbd5e1' }}
                  />
                  <YAxis
                    domain={[-1, 1]}
                    ticks={[-1.0, -0.5, 0, 0.5, 1.0]}
                    tick={{ fontSize: 11, fill: '#64748b' }}
                    tickLine={false}
                    axisLine={{ stroke: '#cbd5e1' }}
                  />
                  <Tooltip
                    content={({ active, payload, label }) => {
                      if (active && payload && payload.length) {
                        const data = payload[0].payload;
                        return (
                          <div className="bg-slate-900 text-white text-xs p-3 rounded-lg shadow-lg border border-slate-800">
                            <p className="font-semibold mb-1 text-slate-200">Date: {data.fullDate}</p>
                            {data.isForecast ? (
                              <div>
                                <p className="text-amber-400 font-bold">
                                  Projected Sentiment: {data.projected > 0 ? `+${data.projected}` : data.projected}
                                </p>
                                <p className="text-[10px] text-slate-400">
                                  Confidence bounds: [{data.lower}, {data.upper}]
                                </p>
                              </div>
                            ) : (
                              <div>
                                <p className="text-indigo-300 font-bold">
                                  Sentiment Score: {data.sentiment > 0 ? `+${data.sentiment}` : data.sentiment}
                                </p>
                                <p className="text-slate-400">Volume: {data.volume} records</p>
                              </div>
                            )}
                          </div>
                        );
                      }
                      return null;
                    }}
                  />
                  <ReferenceLine y={0} stroke="#94a3b8" strokeDasharray="3 3" />
                  
                  {/* Historical sentiment */}
                  <Line
                    type="monotone"
                    dataKey="sentiment"
                    stroke="#4f46e5"
                    strokeWidth={2.5}
                    dot={{ r: 3, fill: '#4f46e5' }}
                    activeDot={{ r: 6 }}
                    name="Observed Polarity"
                  />

                  {/* Projected forecast if present */}
                  {forecast.available && (
                    <Line
                      type="monotone"
                      dataKey="projected"
                      stroke="#d97706"
                      strokeWidth={2}
                      strokeDasharray="4 4"
                      dot={{ r: 3, fill: '#d97706' }}
                      name="Projected Forecast"
                    />
                  )}
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* AI Narrative */}
            {trendNarrative && (
              <div className="bg-slate-50 p-3 rounded-lg border border-slate-200 text-xs text-slate-600 leading-relaxed">
                <span className="font-semibold text-slate-800 block mb-1">Observed Momentum Trend:</span>
                {trendNarrative}
              </div>
            )}
          </div>
        ) : (
          <div className="h-48 flex items-center justify-center text-xs text-slate-400">
            Temporal time-series data points not available for this query.
          </div>
        )}
      </Card>

      {/* 2. Statistical Forecasting & Projection */}
      <Card
        title="Predictive Trajectory"
        subtitle="Linear regression momentum & statistical projection."
      >
        <div className="space-y-4">
          {forecast.available ? (
            <div className="space-y-4">
              <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 flex items-center justify-between">
                <div>
                  <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-0.5">
                    Trend Trajectory
                  </span>
                  <div className="flex items-center gap-2">
                    {getTrendIcon()}
                    <span className="font-bold text-slate-900 text-base capitalize">
                      {forecast.trend_direction.toLowerCase()} Momentum
                    </span>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-0.5">
                    Confidence
                  </span>
                  <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${
                    forecast.confidence === 'HIGH' ? 'bg-emerald-100 text-emerald-800' :
                    forecast.confidence === 'MEDIUM' ? 'bg-blue-100 text-blue-800' :
                    'bg-slate-200 text-slate-700'
                  }`}>
                    {forecast.confidence}
                  </span>
                </div>
              </div>

              <div className="text-xs text-slate-600 space-y-2">
                <p>
                  <span className="font-semibold text-slate-800">Slope Velocity: </span>
                  <code className="font-mono text-slate-700 bg-slate-100 px-1 py-0.5 rounded">
                    {forecast.slope > 0 ? `+${forecast.slope.toFixed(4)}` : forecast.slope.toFixed(4)} / day
                  </code>
                </p>
                <p className="text-slate-500 text-[11px] leading-relaxed">
                  {forecast.reason}
                </p>
              </div>

              {forecastInterpretation && (
                <div className="bg-amber-50/60 p-3 rounded-lg border border-amber-200/60 text-xs text-amber-900 leading-relaxed">
                  <span className="font-semibold text-amber-950 block mb-1">Interpretation Note:</span>
                  {forecastInterpretation}
                </div>
              )}
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-center py-8">
              <AlertCircle className="w-8 h-8 text-slate-400 mx-auto mb-2" />
              <h4 className="text-xs font-bold text-slate-700 mb-1">
                Forecasting Unavailable
              </h4>
              <p className="text-[11px] text-slate-500 leading-relaxed max-w-xs mx-auto">
                {forecast.reason ||
                  'Insufficient longitudinal time-series data points (minimum 3 distinct chronological intervals required) to produce a reliable regression projection.'}
              </p>
            </div>
          )}
        </div>
      </Card>

    </div>
  );
};
