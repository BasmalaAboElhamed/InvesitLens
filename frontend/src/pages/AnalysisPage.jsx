import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Activity, AlertTriangle, BarChart2, CheckCircle2, XCircle,
  Loader2, FileText, Briefcase
} from 'lucide-react';
import useAllAnalyses, {
  isInProgress, formatDateTime, formatDuration
} from '../utils/useAllAnalyses';
import './ListingPages.css';

const FILTERS = [
  { id: 'all', label: 'All' },
  { id: 'running', label: 'Running' },
  { id: 'completed', label: 'Completed' },
  { id: 'failed', label: 'Failed' },
];

const matchesFilter = (run, filter) => {
  if (filter === 'running') return isInProgress(run.status);
  if (filter === 'completed') return run.status === 'completed';
  if (filter === 'failed') return run.status === 'failed';
  return true;
};

const StatusBadge = ({ status }) => {
  if (status === 'completed') {
    return <span className="badge badge-success"><CheckCircle2 size={12} /> Completed</span>;
  }
  if (status === 'failed') {
    return <span className="badge badge-danger"><XCircle size={12} /> Failed</span>;
  }
  return <span className="badge badge-warning"><Loader2 size={12} className="spin" /> {status}</span>;
};

const RiskChips = ({ risk }) => {
  if (!risk) return null;
  const tiers = [
    { label: 'Critical', count: risk.critical_risk_count, cls: 'badge-danger' },
    { label: 'High', count: risk.high_risk_count, cls: 'badge-warning' },
    { label: 'Medium', count: risk.medium_risk_count, cls: 'badge-neutral' },
    { label: 'Low', count: risk.low_risk_count, cls: 'badge-success' },
  ];
  return (
    <div className="risk-chips" aria-label="Risk counts by severity">
      {tiers.map(t => (
        <span key={t.label} className={`badge ${t.cls}`}>{t.count || 0} {t.label}</span>
      ))}
    </div>
  );
};

const RunCard = ({ run }) => {
  const running = isInProgress(run.status);
  const duration = formatDuration(run.started_at, run.completed_at);
  const workspace = `/company/${run.company_id}`;

  return (
    <article className="run-card card card-glass">
      <div className="run-company">
        <div className="run-avatar" aria-hidden="true">
          {run.company_name?.charAt(0).toUpperCase()}
        </div>
        <div style={{ minWidth: 0 }}>
          <h3 className="run-company-name">{run.company_name}</h3>
          <p className="run-meta">
            Started {formatDateTime(run.started_at)}{duration ? ` · took ${duration}` : ''}
          </p>
        </div>
      </div>

      <div>
        <div className="run-status-row">
          <StatusBadge status={run.status} />
          {run.company?.ticker && <span className="badge badge-primary">{run.company.ticker}</span>}
        </div>

        {running && (
          <>
            <div className="progress-track" role="progressbar" aria-valuenow={run.progress || 0} aria-valuemin={0} aria-valuemax={100}>
              <div className="progress-fill" style={{ width: `${run.progress || 0}%` }} />
            </div>
            <p className="run-step">{run.current_step || 'Working…'} ({run.progress || 0}%)</p>
          </>
        )}
        {run.status === 'failed' && run.error_message && (
          <p className="run-error">{run.error_message}</p>
        )}
        {run.status === 'completed' && <RiskChips risk={run.risk_analysis} />}
      </div>

      <div className="run-actions">
        {run.status === 'completed' && (
          <>
            <Link to={`${workspace}/financials`} className="btn btn-secondary btn-sm">
              <BarChart2 size={14} /><span>Financials</span>
            </Link>
            <Link to={`${workspace}/risks`} className="btn btn-secondary btn-sm">
              <AlertTriangle size={14} /><span>Risk Intel</span>
            </Link>
            {run.report && (
              <Link to={`/report/${run.id}`} className="btn btn-primary btn-sm">
                <FileText size={14} /><span>View Report</span>
              </Link>
            )}
          </>
        )}
        {run.status !== 'completed' && (
          <Link to={workspace} className="btn btn-secondary btn-sm">
            <Briefcase size={14} /><span>Open Workspace</span>
          </Link>
        )}
      </div>
    </article>
  );
};

const AnalysisPage = () => {
  const { runs, loading, error, reload } = useAllAnalyses({ pollMs: 4000 });
  const [filter, setFilter] = useState('all');

  const visible = runs.filter(run => matchesFilter(run, filter));
  const runningCount = runs.filter(r => isInProgress(r.status)).length;

  return (
    <div className="listing-page">
      <div className="container">
        <header className="listing-header">
          <div>
            <h1 className="listing-title">Analysis</h1>
            <p className="listing-subtitle">
              {loading
                ? 'Loading analysis runs…'
                : `${runs.length} run${runs.length !== 1 ? 's' : ''} across all workspaces${runningCount ? ` · ${runningCount} in progress` : ''}`}
            </p>
          </div>
          <div className="listing-filters" role="tablist" aria-label="Filter analyses">
            {FILTERS.map(f => (
              <button
                key={f.id}
                role="tab"
                aria-selected={filter === f.id}
                className={`filter-chip${filter === f.id ? ' active' : ''}`}
                onClick={() => setFilter(f.id)}
              >
                {f.label}
              </button>
            ))}
          </div>
        </header>

        {loading ? (
          <div className="listing-stack" aria-busy="true">
            {[0, 1, 2].map(i => (
              <div key={i} className="card skeleton" style={{ height: 96 }} />
            ))}
          </div>
        ) : error ? (
          <div className="empty-state card card-glass">
            <div className="empty-state-icon"><AlertTriangle size={28} /></div>
            <h3>Couldn't load analyses</h3>
            <p className="text-muted">Check that the backend is running, then try again.</p>
            <button className="btn btn-primary mt-4" onClick={() => reload()}>Retry</button>
          </div>
        ) : visible.length === 0 ? (
          <div className="empty-state card card-glass">
            <div className="empty-state-icon"><Activity size={28} /></div>
            <h3>{runs.length === 0 ? 'No analyses yet' : 'No analyses match this filter'}</h3>
            <p className="text-muted" style={{ maxWidth: 380 }}>
              {runs.length === 0
                ? 'Open a workspace, upload documents and press “Run Analysis” to see results here.'
                : 'Try a different filter.'}
            </p>
            {runs.length === 0 && (
              <Link to="/" className="btn btn-primary mt-4">Go to Workspaces</Link>
            )}
          </div>
        ) : (
          <div className="listing-stack">
            {visible.map(run => <RunCard key={run.id} run={run} />)}
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisPage;
