import React from 'react';
import { Building2, CheckCircle2, Clock, Sparkles, FileText, Activity } from 'lucide-react';
import { format, formatDistanceToNow } from 'date-fns';

const CompanyOverview = ({ company, latestAnalysis }) => {
  if (!company) return null;

  return (
    <div className="module-container animate-in">
      <header className="module-header" aria-labelledby="overview-title">
        <h2 id="overview-title" className="text-2xl font-bold tracking-tight text-gradient-subtle">
          Company Overview
        </h2>
        <p className="text-muted mt-1">Summary and analysis status for {company.name}</p>
      </header>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* ── Left Column: Details ── */}
        <div className="lg:col-span-1 flex flex-col gap-6">
          <section className="card card-glass" aria-labelledby="details-heading">
            <h3 id="details-heading" className="text-base font-semibold mb-5 flex items-center gap-2">
              <Building2 size={16} className="text-primary" aria-hidden="true" />
              Company Details
            </h3>
            
            <dl className="space-y-4">
              <div>
                <dt className="text-xs font-semibold text-muted uppercase tracking-wide mb-1">Name</dt>
                <dd className="font-medium">{company.name}</dd>
              </div>
              
              {company.ticker && (
                <div>
                  <dt className="text-xs font-semibold text-muted uppercase tracking-wide mb-1">Ticker</dt>
                  <dd><span className="badge badge-primary">{company.ticker}</span></dd>
                </div>
              )}
              
              <div>
                <dt className="text-xs font-semibold text-muted uppercase tracking-wide mb-1">Industry</dt>
                <dd className="font-medium text-secondary">{company.industry || 'Not specified'}</dd>
              </div>
              
              <div>
                <dt className="text-xs font-semibold text-muted uppercase tracking-wide mb-1">Created</dt>
                <dd className="font-medium text-sm text-slate-300">
                  {company.created_at ? format(new Date(company.created_at), 'MMM d, yyyy') : 'Unknown'}
                </dd>
              </div>
            </dl>
          </section>
          
          <section className="card card-glass" aria-labelledby="status-heading">
            <h3 id="status-heading" className="text-base font-semibold mb-4 text-muted">Workspace Status</h3>
            
            <div className="flex justify-between items-center mb-4 pb-4 border-b border-hover">
              <span className="flex items-center gap-2 text-sm text-muted">
                <FileText size={14} /> Documents
              </span>
              <span className="font-bold text-lg">{company.document_count ?? 0}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="flex items-center gap-2 text-sm text-muted">
                <Activity size={14} /> Analyses Run
              </span>
              <span className="font-bold text-lg">{company.analysis_count ?? 0}</span>
            </div>
          </section>
        </div>

        {/* ── Right Column: Analysis Summary ── */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          {latestAnalysis ? (
            <>
              {latestAnalysis.status === 'completed' ? (
                <section className="card card-glass card-primary" aria-labelledby="intelligence-heading">
                  <header className="flex justify-between items-start mb-6 flex-wrap gap-4">
                    <h3 id="intelligence-heading" className="text-xl font-bold flex items-center gap-2 text-gradient">
                      <Sparkles size={18} className="text-primary" aria-hidden="true" />
                      Latest Intelligence Overview
                    </h3>
                    <div className="flex items-center gap-2 text-xs font-medium text-muted bg-slate-800/50 px-2 py-1 rounded-md">
                      <CheckCircle2 size={12} className="text-success" />
                      {formatDistanceToNow(new Date(latestAnalysis.completed_at || latestAnalysis.started_at), { addSuffix: true })}
                    </div>
                  </header>
                  
                  {latestAnalysis.company_analysis ? (
                    <div className="space-y-6">
                      <div>
                        <h4 className="section-label">Business Model</h4>
                        <p className="leading-relaxed text-[0.9375rem]">{latestAnalysis.company_analysis.business_model}</p>
                      </div>
                      
                      <div>
                        <h4 className="section-label">Products & Services</h4>
                        <p className="leading-relaxed text-[0.9375rem]">{latestAnalysis.company_analysis.products_and_services}</p>
                      </div>
                      
                      <div className="p-5 bg-primary-soft border border-primary-glow rounded-lg relative overflow-hidden">
                        <div className="absolute top-0 right-0 p-3 opacity-20 pointer-events-none">
                          <Sparkles size={48} className="text-primary" />
                        </div>
                        <h4 className="font-bold text-primary mb-2 flex items-center gap-2">
                          AI Executive Summary
                        </h4>
                        <p className="text-[0.9375rem] leading-relaxed relative z-10 text-primary-light">
                          {latestAnalysis.company_analysis.summary}
                        </p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-muted italic">Overview data is not available in this analysis run.</p>
                  )}
                </section>
              ) : (
                <section className="card card-glass border-warning bg-warning-soft" aria-labelledby="progress-heading">
                  <div className="flex items-start gap-4">
                    <div className="p-3 bg-warning/20 text-warning rounded-lg flex-shrink-0 animate-pulse">
                      <Clock size={24} aria-hidden="true" />
                    </div>
                    <div className="flex-1">
                      <h3 id="progress-heading" className="text-lg font-bold text-warning mb-1">
                        Analysis in Progress
                      </h3>
                      <p className="text-sm font-medium mb-1">
                        Status: <span className="capitalize">{latestAnalysis.status}</span>
                      </p>
                      <p className="text-sm text-muted mb-4">{latestAnalysis.current_step || 'Initializing engines...'}</p>
                      
                      <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
                        <div 
                          className="bg-warning h-full rounded-full transition-all duration-500 ease-out" 
                          style={{ width: `${latestAnalysis.progress || 10}%` }}
                          role="progressbar"
                          aria-valuenow={latestAnalysis.progress || 10}
                          aria-valuemin="0"
                          aria-valuemax="100"
                        />
                      </div>
                    </div>
                  </div>
                </section>
              )}
            </>
          ) : (
            <div className="card card-glass empty-state h-full" style={{ minHeight: 400 }}>
              <div className="empty-state-icon" aria-hidden="true">
                <FileText size={32} />
              </div>
              <h3 className="text-xl font-bold mb-2">No Analysis Yet</h3>
              <p className="text-muted max-w-md">
                Upload company documents and run your first AI analysis to generate automated insights and summaries.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompanyOverview;
