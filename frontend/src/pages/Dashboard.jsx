import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Plus, Briefcase, FileText, Activity, AlertTriangle,
  ChevronRight, X, Search, Sparkles
} from 'lucide-react';
import { companyService } from '../services/api';
import './Dashboard.css';

/* ── Skeleton card for loading state ── */
const WorkspaceSkeleton = () => (
  <div className="workspace-card card" aria-hidden="true">
    <div className="skeleton" style={{ height: 20, width: '60%', marginBottom: 12, borderRadius: 6 }} />
    <div className="skeleton" style={{ height: 14, width: '35%', marginBottom: 24, borderRadius: 6 }} />
    <div className="skeleton" style={{ height: 14, width: '80%', marginBottom: 8, borderRadius: 6 }} />
    <div className="skeleton" style={{ height: 14, width: '55%', borderRadius: 6 }} />
  </div>
);

const Dashboard = () => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [newCompany, setNewCompany] = useState({ name: '', industry: '', ticker: '' });
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  useEffect(() => {
    fetchCompanies();
  }, []);

  const fetchCompanies = async () => {
    try {
      setLoading(true);
      const data = await companyService.getCompanies();
      setCompanies(data);
    } catch (error) {
      console.error('Failed to fetch companies', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateCompany = async (e) => {
    e.preventDefault();
    if (creating) return;
    try {
      setCreating(true);
      const created = await companyService.createCompany(newCompany);
      setShowModal(false);
      setNewCompany({ name: '', industry: '', ticker: '' });
      navigate(`/company/${created.id}`);
    } catch (error) {
      console.error('Failed to create company', error);
    } finally {
      setCreating(false);
    }
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setNewCompany({ name: '', industry: '', ticker: '' });
  };

  const totalDocs = companies.reduce((a, c) => a + (c.document_count || 0), 0);
  const totalAnalyses = companies.reduce((a, c) => a + (c.analysis_count || 0), 0);
  const totalRisks = companies.reduce((a, c) => a + (c.high_risk_count || 0), 0);

  const filtered = companies.filter(c =>
    !searchQuery ||
    c.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.ticker?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    c.industry?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="dashboard">
      {/* ── Hero Section ── */}
      <section className="dashboard-hero" aria-labelledby="hero-heading">
        <div className="hero-glow" aria-hidden="true" />
        <div className="container">
          <div className="hero-content animate-in">
            <div className="hero-label">
              <Sparkles size={12} />
              <span>AI Investment Intelligence</span>
            </div>
            <h1 id="hero-heading" className="hero-title text-gradient-subtle tracking-tight">
              Investor Intelligence<br />
              <span className="text-gradient">Powered by AI</span>
            </h1>
            <p className="hero-subtitle">
              Upload financial reports, run multi-agent analysis, and get evidence-grounded insights.
              Built for investors who demand precision.
            </p>
            <div className="hero-actions">
              <button
                id="btn-new-workspace"
                className="btn btn-primary btn-lg"
                onClick={() => setShowModal(true)}
                aria-label="Create new workspace"
              >
                <Plus size={18} strokeWidth={2.5} />
                <span>New Workspace</span>
              </button>
              <a
                href="#workspaces"
                className="btn btn-secondary btn-lg"
              >
                <Briefcase size={16} />
                <span>View Workspaces</span>
              </a>
            </div>
          </div>
        </div>
      </section>

      {/* ── Stats Row ── */}
      <section className="container" aria-label="Overview statistics">
        <div className="stats-grid animate-in delay-1">
          <StatCard
            icon={<Briefcase size={20} />}
            value={companies.length}
            label="Companies"
            color="purple"
            loading={loading}
          />
          <StatCard
            icon={<FileText size={20} />}
            value={totalDocs}
            label="Documents"
            color="cyan"
            loading={loading}
          />
          <StatCard
            icon={<Activity size={20} />}
            value={totalAnalyses}
            label="Analyses Run"
            color="green"
            loading={loading}
          />
          <StatCard
            icon={<AlertTriangle size={20} />}
            value={totalRisks}
            label="High Risks"
            color="red"
            loading={loading}
          />
        </div>
      </section>

      {/* ── Workspaces ── */}
      <section id="workspaces" className="container workspaces-section" aria-labelledby="workspaces-heading">
        <div className="section-header animate-in delay-2">
          <div>
            <h2 id="workspaces-heading">Active Workspaces</h2>
            <p className="text-muted text-sm mt-1">
              {companies.length > 0 ? `${companies.length} workspace${companies.length !== 1 ? 's' : ''} tracked` : 'No workspaces yet'}
            </p>
          </div>
          {companies.length > 0 && (
            <div className="search-box">
              <Search size={15} className="search-icon" aria-hidden="true" />
              <input
                type="text"
                id="workspace-search"
                placeholder="Search workspaces..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="search-input"
                aria-label="Search workspaces"
              />
            </div>
          )}
        </div>

        {loading ? (
          <div className="workspaces-grid" aria-busy="true" aria-label="Loading workspaces">
            {[...Array(3)].map((_, i) => <WorkspaceSkeleton key={i} />)}
          </div>
        ) : filtered.length === 0 && searchQuery ? (
          <div className="empty-state card card-glass animate-in">
            <div className="empty-state-icon">
              <Search size={28} />
            </div>
            <h3>No results found</h3>
            <p className="text-muted">Try adjusting your search query.</p>
            <button className="btn btn-ghost mt-4" onClick={() => setSearchQuery('')}>
              Clear search
            </button>
          </div>
        ) : companies.length === 0 ? (
          <div className="empty-state card card-glass animate-in">
            <div className="empty-state-icon">
              <Briefcase size={28} />
            </div>
            <h3>No workspaces yet</h3>
            <p className="text-muted" style={{ maxWidth: 360 }}>
              Create your first company workspace to start uploading documents and running AI analysis.
            </p>
            <button
              id="btn-create-first"
              className="btn btn-primary mt-4"
              onClick={() => setShowModal(true)}
            >
              <Plus size={16} />
              <span>Create Workspace</span>
            </button>
          </div>
        ) : (
          <div className="workspaces-grid animate-in delay-3">
            {filtered.map((company, i) => (
              <WorkspaceCard
                key={company.id}
                company={company}
                index={i}
                onClick={() => navigate(`/company/${company.id}`)}
              />
            ))}
          </div>
        )}
      </section>

      {/* ── Create Modal ── */}
      {showModal && (
        <div
          className="modal-overlay"
          role="dialog"
          aria-modal="true"
          aria-labelledby="modal-title"
          onClick={e => { if (e.target === e.currentTarget) handleCloseModal(); }}
        >
          <div className="modal-content card card-glass">
            <div className="modal-header">
              <div>
                <h2 id="modal-title" className="text-xl">New Workspace</h2>
                <p className="text-muted text-sm mt-1">Add a company to begin intelligence analysis</p>
              </div>
              <button
                className="btn btn-ghost btn-icon"
                onClick={handleCloseModal}
                aria-label="Close modal"
              >
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleCreateCompany}>
              <div className="form-group">
                <label className="form-label" htmlFor="company-name">
                  Company Name <span style={{ color: 'var(--danger)' }}>*</span>
                </label>
                <input
                  id="company-name"
                  type="text"
                  className="form-control"
                  value={newCompany.name}
                  onChange={e => setNewCompany({ ...newCompany, name: e.target.value })}
                  required
                  placeholder="e.g. Apple Inc."
                  autoFocus
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="company-industry">Industry</label>
                <input
                  id="company-industry"
                  type="text"
                  className="form-control"
                  value={newCompany.industry}
                  onChange={e => setNewCompany({ ...newCompany, industry: e.target.value })}
                  placeholder="e.g. Technology"
                />
              </div>
              <div className="form-group">
                <label className="form-label" htmlFor="company-ticker">Ticker Symbol</label>
                <input
                  id="company-ticker"
                  type="text"
                  className="form-control"
                  value={newCompany.ticker}
                  onChange={e => setNewCompany({ ...newCompany, ticker: e.target.value.toUpperCase() })}
                  placeholder="e.g. AAPL"
                />
              </div>
              <div className="modal-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={handleCloseModal}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  id="btn-create-submit"
                  className="btn btn-primary"
                  disabled={creating || !newCompany.name.trim()}
                >
                  {creating ? (
                    <>
                      <span className="spinner spinner-sm" aria-hidden="true" />
                      <span>Creating…</span>
                    </>
                  ) : (
                    <>
                      <Plus size={15} />
                      <span>Create Workspace</span>
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

/* ── Stat Card sub-component ── */
const StatCard = ({ icon, value, label, color, loading }) => {
  const colorMap = {
    purple: 'var(--primary)',
    cyan:   'var(--secondary)',
    green:  'var(--success)',
    red:    'var(--danger)',
  };
  const bgMap = {
    purple: 'var(--primary-soft)',
    cyan:   'var(--secondary-soft)',
    green:  'var(--success-soft)',
    red:    'var(--danger-soft)',
  };
  const c = colorMap[color] || colorMap.purple;
  const bg = bgMap[color] || bgMap.purple;

  return (
    <div className="stat-card card">
      <div className="stat-icon-wrap" style={{ background: bg, color: c }}>
        {icon}
      </div>
      <div className="stat-body">
        {loading ? (
          <div className="skeleton" style={{ height: 28, width: 48, borderRadius: 6 }} />
        ) : (
          <span className="stat-value">{value}</span>
        )}
        <span className="stat-label">{label}</span>
      </div>
    </div>
  );
};

/* ── Workspace Card sub-component ── */
const WorkspaceCard = ({ company, onClick, index }) => (
  <article
    className="workspace-card card card-interactive"
    onClick={onClick}
    style={{ animationDelay: `${0.04 * index}s` }}
    tabIndex={0}
    role="button"
    aria-label={`Open ${company.name} workspace`}
    onKeyDown={e => (e.key === 'Enter' || e.key === ' ') && onClick()}
  >
    <div className="wc-header">
      <div className="wc-avatar" aria-hidden="true">
        {company.name?.charAt(0).toUpperCase()}
      </div>
      <div className="wc-chevron" aria-hidden="true">
        <ChevronRight size={16} />
      </div>
    </div>

    <div className="wc-info">
      <div className="wc-title-row">
        <h3 className="wc-name">{company.name}</h3>
        {company.ticker && (
          <span className="badge badge-primary">{company.ticker}</span>
        )}
      </div>
      <p className="wc-industry text-muted text-sm">
        {company.industry || 'Industry not set'}
      </p>
    </div>

    <div className="wc-metrics">
      <div className="wc-metric">
        <FileText size={13} className="text-muted" />
        <span className="text-sm">{company.document_count ?? 0} docs</span>
      </div>
      <div className="wc-metric">
        <Activity size={13} className="text-muted" />
        <span className="text-sm">{company.analysis_count ?? 0} runs</span>
      </div>
      {(company.high_risk_count ?? 0) > 0 && (
        <div className="wc-metric" style={{ color: 'var(--danger)' }}>
          <AlertTriangle size={13} />
          <span className="text-sm">{company.high_risk_count} risks</span>
        </div>
      )}
    </div>
  </article>
);

export default Dashboard;
