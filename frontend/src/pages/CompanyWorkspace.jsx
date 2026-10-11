import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Routes, Route, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Building2, FileText, BarChart2, Activity, AlertTriangle,
  TrendingUp, MessageSquare, Play, ExternalLink, ChevronLeft,
  Loader2, PanelLeft
} from 'lucide-react';
import { companyService, documentService, analysisService } from '../services/api';
import CompanyOverview from '../components/CompanyOverview';
import DocumentsManager from '../components/DocumentsManager';
import ChatInterface from '../components/ChatInterface';
import AnalysisDashboard from '../components/AnalysisDashboard';
import './CompanyWorkspace.css';

const CompanyWorkspace = () => {
  const { companyId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();

  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);
  const [documents, setDocuments] = useState([]);
  const [analyses, setAnalyses] = useState([]);
  const [analysisRunning, setAnalysisRunning] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const fetchCompanyData = useCallback(async () => {
    try {
      setLoading(true);
      const [compData, docsData, analData] = await Promise.all([
        companyService.getCompany(companyId),
        documentService.getCompanyDocuments(companyId),
        analysisService.getCompanyAnalyses(companyId),
      ]);
      setCompany(compData);
      setDocuments(docsData);
      setAnalyses(analData);
    } catch (error) {
      console.error('Failed to fetch company data', error);
    } finally {
      setLoading(false);
    }
  }, [companyId]);

  useEffect(() => {
    fetchCompanyData();
  }, [fetchCompanyData]);

  // While an analysis is running, quietly refresh its status every few seconds
  // so the Financials / Trends / Risk Intel pages fill in by themselves.
  useEffect(() => {
    const inProgress = analyses.some(a =>
      ['uploading', 'processing', 'indexing', 'analyzing'].includes(a.status)
    );
    if (!inProgress) return undefined;

    const timer = setTimeout(async () => {
      try {
        setAnalyses(await analysisService.getCompanyAnalyses(companyId));
      } catch (error) {
        console.error('Failed to refresh analysis status', error);
      }
    }, 4000);
    return () => clearTimeout(timer);
  }, [analyses, companyId]);

  const handleStartAnalysis = async () => {
    if (documents.length === 0) {
      alert('Please upload at least one document before running analysis.');
      return;
    }
    try {
      setAnalysisRunning(true);
      const newAnalysis = await analysisService.startAnalysis(companyId);
      setAnalyses(prev => [...prev, newAnalysis]);
    } catch (error) {
      console.error('Failed to start analysis', error);
      alert('Failed to start analysis: ' + (error.response?.data?.detail || error.message));
    } finally {
      setAnalysisRunning(false);
    }
  };

  // Determine active tab from path
  const pathParts = location.pathname.split('/');
  const lastPart = pathParts[pathParts.length - 1];
  const activeTab = (lastPart === companyId || lastPart === '') ? 'overview' : lastPart;

  const latestAnalysis = analyses.length > 0
    ? [...analyses].sort((a, b) => new Date(b.started_at) - new Date(a.started_at))[0]
    : null;

  if (loading) {
    return (
      <div className="loading-state">
        <span className="spinner spinner-lg" aria-label="Loading workspace" />
        <p>Loading workspace…</p>
      </div>
    );
  }

  if (!company) {
    return (
      <div className="error-page">
        <Building2 size={48} className="text-muted" />
        <h2>Workspace not found</h2>
        <p className="text-muted">This company workspace could not be loaded.</p>
        <Link to="/" className="btn btn-primary mt-6">
          <ChevronLeft size={16} />
          Back to Dashboard
        </Link>
      </div>
    );
  }

  // Absolute paths: relative links resolve against the current sub-page inside
  // this splat route (/company/:id/*), which broke navigation between sections.
  const base = `/company/${companyId}`;

  const navItems = [
    {
      to: base, id: 'overview', icon: <Activity size={17} />, label: 'Overview',
      active: activeTab === 'overview',
      group: null,
    },
    {
      to: `${base}/documents`, id: 'documents', icon: <FileText size={17} />,
      label: `Documents`,
      badge: documents.length > 0 ? documents.length : null,
      active: activeTab === 'documents',
      group: null,
    },
    {
      to: `${base}/financials`, id: 'financials', icon: <BarChart2 size={17} />, label: 'Financials',
      active: activeTab === 'financials',
      group: 'Analysis',
    },
    {
      to: `${base}/trends`, id: 'trends', icon: <TrendingUp size={17} />, label: 'Trends',
      active: activeTab === 'trends',
      group: 'Analysis',
    },
    {
      to: `${base}/risks`, id: 'risks', icon: <AlertTriangle size={17} />, label: 'Risk Intel',
      active: activeTab === 'risks',
      group: 'Analysis',
    },
    {
      to: `${base}/chat`, id: 'chat', icon: <MessageSquare size={17} />, label: 'AI Assistant',
      active: activeTab === 'chat',
      group: 'Interactive',
    },
  ];

  const hasReport = latestAnalysis?.status === 'completed';

  return (
    <div className={`workspace-layout${sidebarOpen ? '' : ' sidebar-collapsed'}`}>
      {/* ── Sidebar ── */}
      <aside className="workspace-sidebar" aria-label="Workspace navigation">
        {/* Company header */}
        <div className="sidebar-company">
          <div className="company-avatar" aria-hidden="true">
            {company.name?.charAt(0).toUpperCase()}
          </div>
          <div className="company-meta">
            <h2 className="company-name">{company.name}</h2>
            {company.ticker && (
              <span className="badge badge-primary company-ticker">{company.ticker}</span>
            )}
          </div>
        </div>

        {/* Navigation */}
        <nav className="sidebar-nav" aria-label="Section navigation">
          {(() => {
            let currentGroup = null;
            return navItems.map(item => {
              const showGroupLabel = item.group && item.group !== currentGroup;
              if (showGroupLabel) currentGroup = item.group;
              return (
                <React.Fragment key={item.id}>
                  {showGroupLabel && (
                    <div className="section-label" aria-hidden="true">{item.group}</div>
                  )}
                  <Link
                    to={item.to}
                    id={`sidebar-${item.id}`}
                    className={`sidebar-link${item.active ? ' active' : ''}`}
                    aria-current={item.active ? 'page' : undefined}
                  >
                    <span className="sidebar-link-icon">{item.icon}</span>
                    <span className="sidebar-link-label">{item.label}</span>
                    {item.badge != null && (
                      <span className="sidebar-badge">{item.badge}</span>
                    )}
                  </Link>
                </React.Fragment>
              );
            });
          })()}
        </nav>

        {/* Sidebar Actions */}
        <div className="sidebar-actions">
          {hasReport && (
            <button
              className="btn btn-secondary w-full justify-between mb-3"
              onClick={() => navigate(`/report/${latestAnalysis.id}`)}
              id="btn-view-report"
            >
              <span>View Full Report</span>
              <ExternalLink size={14} />
            </button>
          )}
          <button
            id="btn-run-analysis"
            className="btn btn-primary w-full justify-between"
            onClick={handleStartAnalysis}
            disabled={documents.length === 0 || analysisRunning}
            aria-label={documents.length === 0 ? 'Upload documents first to run analysis' : 'Run AI analysis'}
          >
            {analysisRunning ? (
              <>
                <span>Analyzing…</span>
                <Loader2 size={15} className="animate-spin" />
              </>
            ) : (
              <>
                <span>Run Analysis</span>
                <Play size={14} strokeWidth={2.5} />
              </>
            )}
          </button>
          {documents.length === 0 && (
            <p className="sidebar-hint">Upload documents to enable analysis</p>
          )}
        </div>
      </aside>

      {/* ── Collapse Toggle (mobile) ── */}
      <button
        className="sidebar-toggle btn btn-ghost btn-icon"
        onClick={() => setSidebarOpen(o => !o)}
        aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
      >
        <PanelLeft size={18} />
      </button>

      {/* ── Main Content ── */}
      <main className="workspace-content" aria-label="Workspace content">
        <Routes>
          <Route path=""           element={<CompanyOverview company={company} latestAnalysis={latestAnalysis} />} />
          <Route path="documents"  element={<DocumentsManager company={company} documents={documents} onDocumentUploaded={fetchCompanyData} />} />
          <Route path="financials" element={<AnalysisDashboard analysis={latestAnalysis} module="financial" />} />
          <Route path="trends"     element={<AnalysisDashboard analysis={latestAnalysis} module="trends" />} />
          <Route path="risks"      element={<AnalysisDashboard analysis={latestAnalysis} module="risks" />} />
          <Route path="chat"       element={<ChatInterface company={company} />} />
        </Routes>
      </main>
    </div>
  );
};

export default CompanyWorkspace;
