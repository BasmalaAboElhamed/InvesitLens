import React from 'react';
import { Link } from 'react-router-dom';
import { AlertTriangle, ArrowRight, FileText, Briefcase } from 'lucide-react';
import useAllAnalyses, { formatDateTime } from '../utils/useAllAnalyses';
import './ListingPages.css';

const ReportCard = ({ run }) => {
  const risk = run.risk_analysis;
  const importantRisks = (risk?.critical_risk_count || 0) + (risk?.high_risk_count || 0);
  const totalRisks = risk?.risks?.length ?? 0;
  const summary = run.report?.executive_summary || run.report?.overall_summary;

  return (
    <article className="report-card card card-glass card-interactive">
      <div className="report-card-head">
        <div className="run-company">
          <div className="run-avatar" aria-hidden="true">
            {run.company_name?.charAt(0).toUpperCase()}
          </div>
          <div style={{ minWidth: 0 }}>
            <h3 className="run-company-name">{run.company_name}</h3>
            <p className="run-meta">{formatDateTime(run.completed_at || run.started_at)}</p>
          </div>
        </div>
        {run.company?.ticker && <span className="badge badge-primary">{run.company.ticker}</span>}
      </div>

      <p className="report-summary">{summary || 'No summary available for this report.'}</p>

      <div className="report-card-foot">
        {importantRisks > 0 ? (
          <span className="badge badge-danger"><AlertTriangle size={12} /> {importantRisks} high/critical risk{importantRisks !== 1 ? 's' : ''}</span>
        ) : (
          <span className="badge badge-neutral">{totalRisks} risk{totalRisks !== 1 ? 's' : ''} identified</span>
        )}
        <div className="run-actions">
          <Link to={`/company/${run.company_id}`} className="btn btn-ghost btn-sm">
            <Briefcase size={14} /><span>Workspace</span>
          </Link>
          <Link to={`/report/${run.id}`} className="btn btn-primary btn-sm">
            <span>Open Report</span><ArrowRight size={14} />
          </Link>
        </div>
      </div>
    </article>
  );
};

const ReportsPage = () => {
  const { runs, loading, error, reload } = useAllAnalyses();
  const reports = runs.filter(run => run.status === 'completed' && run.report);

  return (
    <div className="listing-page">
      <div className="container">
        <header className="listing-header">
          <div>
            <h1 className="listing-title">Reports</h1>
            <p className="listing-subtitle">
              {loading
                ? 'Loading reports…'
                : `${reports.length} intelligence report${reports.length !== 1 ? 's' : ''} generated`}
            </p>
          </div>
        </header>

        {loading ? (
          <div className="report-grid" aria-busy="true">
            {[0, 1, 2].map(i => (
              <div key={i} className="card skeleton" style={{ height: 220 }} />
            ))}
          </div>
        ) : error ? (
          <div className="empty-state card card-glass">
            <div className="empty-state-icon"><AlertTriangle size={28} /></div>
            <h3>Couldn't load reports</h3>
            <p className="text-muted">Check that the backend is running, then try again.</p>
            <button className="btn btn-primary mt-4" onClick={() => reload()}>Retry</button>
          </div>
        ) : reports.length === 0 ? (
          <div className="empty-state card card-glass">
            <div className="empty-state-icon"><FileText size={28} /></div>
            <h3>No reports yet</h3>
            <p className="text-muted" style={{ maxWidth: 380 }}>
              Reports appear here once an analysis finishes. Run an analysis from any workspace to generate one.
            </p>
            <Link to="/" className="btn btn-primary mt-4">Go to Workspaces</Link>
          </div>
        ) : (
          <div className="report-grid">
            {reports.map(run => <ReportCard key={run.id} run={run} />)}
          </div>
        )}
      </div>
    </div>
  );
};

export default ReportsPage;
