import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertTriangle, TrendingUp, DollarSign, Activity, FileText, ChevronRight } from 'lucide-react';

const AnalysisDashboard = ({ analysis, module }) => {
  if (!analysis) {
    return (
      <div className="empty-state h-64 mt-12 animate-in">
        <div className="empty-state-icon text-muted bg-slate-800 border-slate-700">
          <Activity size={32} />
        </div>
        <h3 className="text-xl font-bold mt-2">No data available</h3>
        <p className="text-muted">Run an analysis to see insights here.</p>
      </div>
    );
  }

  if (analysis.status !== 'completed') {
    return (
      <div className="empty-state h-64 mt-12 animate-in">
        <div className="spinner spinner-lg mb-4 text-warning" />
        <h3 className="text-xl font-bold text-warning mt-2">Analysis Running</h3>
        <p className="text-muted">Extracting insights... ({analysis.progress || 10}%)</p>
      </div>
    );
  }

  const renderFinancials = () => {
    const data = analysis.financial_analysis;
    if (!data || !data.insights || data.insights.length === 0) {
      return <p className="text-muted mt-8">No financial insights extracted in this run.</p>;
    }

    const chartData = data.insights
      .filter(i => i.current_value && i.current_value.includes('$') && i.previous_value && i.previous_value.includes('$'))
      .map(i => {
        const currNum = parseFloat(i.current_value.replace(/[^0-9.-]+/g, ""));
        const prevNum = parseFloat(i.previous_value.replace(/[^0-9.-]+/g, ""));
        return {
          name: i.metric,
          Current: isNaN(currNum) ? 0 : currNum,
          Previous: isNaN(prevNum) ? 0 : prevNum
        };
      }).slice(0, 5);

    return (
      <div className="animate-in">
        <header className="module-header flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary-soft text-primary flex items-center justify-center border border-border-accent">
            <DollarSign size={20} />
          </div>
          <h2 className="text-2xl font-bold tracking-tight">Financial Analysis</h2>
        </header>

        {data.summary && (
          <section className="card card-glass card-primary mb-8" aria-labelledby="fin-summary">
            <h3 id="fin-summary" className="text-sm font-bold text-primary uppercase tracking-wide mb-3 flex items-center gap-2">
              <SparkleIcon /> Executive Summary
            </h3>
            <p className="text-[1.0625rem] leading-relaxed text-text-primary font-medium">{data.summary}</p>
          </section>
        )}

        {chartData.length > 0 && (
          <section className="card card-glass mb-8 p-0 overflow-hidden" aria-labelledby="fin-chart">
            <div className="p-5 border-b border-border">
              <h3 id="fin-chart" className="text-base font-bold">Key Metrics Comparison</h3>
            </div>
            <div className="h-72 p-4 pt-6">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                  <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} tickFormatter={v => `$${v}`} />
                  <Tooltip 
                    contentStyle={{ backgroundColor: 'var(--bg-elevated)', borderColor: 'var(--border-hover)', borderRadius: '8px', boxShadow: 'var(--shadow-md)' }}
                    itemStyle={{ color: 'var(--text-primary)', fontWeight: 600 }}
                    labelStyle={{ color: 'var(--text-muted)', marginBottom: '4px' }}
                    cursor={{ fill: 'rgba(255,255,255,0.02)' }}
                  />
                  <Bar dataKey="Previous" fill="var(--text-faint)" radius={[4, 4, 0, 0]} maxBarSize={40} />
                  <Bar dataKey="Current" fill="var(--primary)" radius={[4, 4, 0, 0]} maxBarSize={40} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </section>
        )}

        <h3 className="section-label mb-4">Detailed Metrics</h3>
        <div className="grid md:grid-cols-2 gap-4">
          {data.insights.map((insight, idx) => (
            <article key={idx} className="card card-glass flex flex-col h-full animate-in" style={{ animationDelay: `${idx * 0.05}s` }}>
              <div className="flex justify-between items-start mb-4 gap-4">
                <h4 className="text-base font-bold text-text-primary leading-snug">{insight.metric}</h4>
                <span className={`badge ${insight.change?.includes('-') ? 'badge-danger' : 'badge-success'} flex-shrink-0`}>
                  {insight.change || 'N/A'}
                </span>
              </div>
              
              <div className="grid grid-cols-2 gap-4 mb-4 pb-4 border-b border-border">
                <div>
                  <span className="text-[0.6875rem] font-bold text-muted uppercase tracking-wider block mb-1">Current</span>
                  <span className="font-bold text-xl text-primary">{insight.current_value || 'N/A'}</span>
                </div>
                <div>
                  <span className="text-[0.6875rem] font-bold text-muted uppercase tracking-wider block mb-1">Previous</span>
                  <span className="font-medium text-lg text-text-muted">{insight.previous_value || 'N/A'}</span>
                </div>
              </div>
              
              <p className="text-sm text-text-secondary mb-5 flex-1">{insight.interpretation}</p>
              
              {insight.evidence && (
                <div className="bg-bg-elevated/50 p-3 rounded-md text-xs border-l-2 border-primary-dim mt-auto">
                  <div className="flex items-center gap-1.5 mb-1.5 text-muted font-bold uppercase tracking-wide">
                    <FileText size={10} /> Evidence
                  </div>
                  <p className="italic text-text-secondary line-clamp-3 mb-2">"{insight.evidence}"</p>
                  <div className="text-[0.6875rem] text-muted flex justify-between font-medium">
                    <span className="truncate mr-2">Src: {insight.source || 'Unknown'}</span>
                    <span className="flex-shrink-0">Pg: {insight.page || 'N/A'}</span>
                  </div>
                </div>
              )}
            </article>
          ))}
        </div>
      </div>
    );
  };

  const renderRisks = () => {
    const data = analysis.risk_analysis;
    if (!data || !data.risks || data.risks.length === 0) {
      return <p className="text-muted mt-8">No risks extracted.</p>;
    }

    const severityMap = {
      'Critical': { color: 'var(--danger)', bg: 'var(--danger-soft)', badge: 'badge-danger' },
      'High':     { color: '#F97316', bg: 'rgba(249, 115, 22, 0.1)', badge: 'badge-warning' }, // Using orange for high
      'Medium':   { color: 'var(--warning)', bg: 'var(--warning-soft)', badge: 'badge-warning' },
      'Low':      { color: 'var(--success)', bg: 'var(--success-soft)', badge: 'badge-success' }
    };

    return (
      <div className="animate-in">
        <header className="module-header flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-danger-soft text-danger flex items-center justify-center border border-[rgba(239,68,68,0.2)]">
            <AlertTriangle size={20} />
          </div>
          <h2 className="text-2xl font-bold tracking-tight">Risk Intelligence</h2>
        </header>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {[
            { label: 'Critical', count: data.critical_risk_count, key: 'Critical' },
            { label: 'High', count: data.high_risk_count, key: 'High' },
            { label: 'Medium', count: data.medium_risk_count, key: 'Medium' },
            { label: 'Low', count: data.low_risk_count, key: 'Low' }
          ].map((tier) => {
            const style = severityMap[tier.key];
            return (
              <div key={tier.label} className="card card-glass text-center p-4 border-t-2" style={{ borderTopColor: style.color }}>
                <span className="text-3xl font-bold block leading-none mb-1" style={{ color: style.color }}>{tier.count || 0}</span>
                <span className="text-xs font-bold text-muted uppercase tracking-wider">{tier.label}</span>
              </div>
            );
          })}
        </div>

        {data.summary && (
          <section className="card card-glass mb-8 p-6" style={{ borderLeft: '4px solid var(--warning)' }}>
            <h3 className="text-sm font-bold text-warning uppercase tracking-wide mb-3 flex items-center gap-2">
              <AlertTriangle size={14} /> Risk Overview
            </h3>
            <p className="text-[1.0625rem] leading-relaxed text-text-primary font-medium">{data.summary}</p>
          </section>
        )}

        <h3 className="section-label mb-4">Identified Risks</h3>
        <div className="grid gap-4">
          {data.risks.sort((a, b) => {
            const val = { 'Critical': 4, 'High': 3, 'Medium': 2, 'Low': 1 };
            return (val[b.severity] || 0) - (val[a.severity] || 0);
          }).map((risk, idx) => {
            const style = severityMap[risk.severity] || severityMap['Medium'];
            return (
              <article key={idx} className="card card-glass animate-in flex flex-col md:flex-row gap-5" style={{ animationDelay: `${idx * 0.05}s` }}>
                <div className="md:w-1/3 flex flex-col gap-3 border-b md:border-b-0 md:border-r border-border pb-4 md:pb-0 md:pr-5">
                  <div className="flex gap-2 flex-wrap">
                    <span className={`badge ${style.badge}`}>{risk.severity}</span>
                    <span className="badge badge-neutral">{risk.category}</span>
                  </div>
                  <h4 className="text-[1.0625rem] font-bold text-text-primary leading-snug">{risk.risk}</h4>
                </div>
                
                <div className="md:w-2/3 flex flex-col">
                  <p className="text-sm text-text-secondary mb-3">{risk.explanation}</p>
                  
                  {risk.potential_impact && (
                    <div className="mb-4 text-sm bg-bg-elevated/40 p-3 rounded-md">
                      <span className="font-semibold text-text-primary text-xs uppercase tracking-wide block mb-1">Potential Impact</span>
                      <span className="text-text-secondary">{risk.potential_impact}</span>
                    </div>
                  )}
                  
                  {risk.evidence && (
                    <div className="mt-auto text-xs">
                      <div className="flex flex-col gap-1 text-muted border-l-2 pl-3" style={{ borderColor: style.color }}>
                        <p className="italic line-clamp-2 mb-1">"{risk.evidence}"</p>
                        <div className="flex justify-between font-medium">
                          <span className="truncate">Source: {risk.source || 'Unknown'}</span>
                          <span>Pg: {risk.page || 'N/A'}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </article>
            );
          })}
        </div>
      </div>
    );
  };

  const renderTrends = () => {
    const data = analysis.trend_analysis;
    if (!data || !data.trends || data.trends.length === 0) {
      return <p className="text-muted mt-8">No trend data available.</p>;
    }

    return (
      <div className="animate-in">
        <header className="module-header flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-cyan-soft text-cyan flex items-center justify-center border border-[rgba(34,211,238,0.2)]">
            <TrendingUp size={20} />
          </div>
          <h2 className="text-2xl font-bold tracking-tight">Trend Analysis</h2>
        </header>
        
        {data.summary && (
          <section className="card card-glass mb-8 p-6" style={{ borderLeft: '4px solid var(--secondary)' }}>
            <p className="text-[1.0625rem] leading-relaxed text-text-primary font-medium">{data.summary}</p>
          </section>
        )}

        <div className="grid md:grid-cols-2 gap-4">
          {data.trends.map((trend, idx) => (
            <article key={idx} className="card card-glass flex flex-col animate-in" style={{ animationDelay: `${idx * 0.05}s` }}>
              <div className="flex justify-between items-start mb-4 gap-4">
                <h4 className="text-base font-bold text-cyan leading-snug">{trend.metric}</h4>
                <span className={`badge flex-shrink-0 ${trend.direction === 'Increasing' ? 'badge-success' : trend.direction === 'Decreasing' ? 'badge-danger' : 'badge-warning'}`}>
                  {trend.direction}
                </span>
              </div>
              
              <p className="text-sm text-text-secondary mb-5 flex-1">{trend.interpretation}</p>
              
              {trend.evidence && (
                <div className="bg-bg-elevated/50 p-3 rounded-md text-xs border-l-2 border-secondary-soft mt-auto">
                  <p className="italic text-text-secondary line-clamp-3 mb-2">"{trend.evidence}"</p>
                  <div className="text-[0.6875rem] text-muted font-medium truncate">
                    Src: {trend.source || 'Unknown'}
                  </div>
                </div>
              )}
            </article>
          ))}
        </div>
      </div>
    );
  };

  switch (module) {
    case 'financial': return renderFinancials();
    case 'risks': return renderRisks();
    case 'trends': return renderTrends();
    default: return <p>Select a module</p>;
  }
};

const SparkleIcon = () => (
  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"/>
  </svg>
);

export default AnalysisDashboard;
