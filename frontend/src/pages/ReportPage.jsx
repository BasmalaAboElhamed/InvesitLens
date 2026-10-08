import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FileText, ArrowLeft, Download, AlertTriangle, TrendingUp, DollarSign, Sparkles, Building2 } from 'lucide-react';
import { reportService, companyService } from '../services/api';
import './ReportPage.css';

const ReportPage = () => {
  const { analysisId } = useParams();
  const [report, setReport] = useState(null);
  const [company, setCompany] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReport();
  }, [analysisId]);

  const fetchReport = async () => {
    try {
      setLoading(true);
      const reportData = await reportService.getReport(analysisId);
      setReport(reportData);
      
      const companies = await companyService.getCompanies();
      const comp = companies.find(c => c.name === reportData.company);
      if (comp) setCompany(comp);
      
    } catch (error) {
      console.error("Failed to fetch report", error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return (
    <div className="loading-state h-screen">
      <div className="spinner spinner-lg text-primary mb-4"></div>
      <p className="text-muted font-medium">Generating intelligence report...</p>
    </div>
  );

  if (!report) return (
    <div className="empty-state h-screen">
      <div className="empty-state-icon">
        <FileText size={32} />
      </div>
      <h2 className="text-2xl font-bold mb-2">Report Not Found</h2>
      <p className="text-muted mb-6">The requested intelligence report could not be loaded.</p>
      <Link to="/" className="btn btn-primary">Return to Dashboard</Link>
    </div>
  );

  return (
    <div className="report-layout">
      {/* ── Top Nav Actions ── */}
      <div className="report-nav container mx-auto">
        <Link 
          to={company ? `/company/${company.id}` : "/"} 
          className="btn btn-secondary btn-sm"
        >
          <ArrowLeft size={14} />
          <span>Back to Workspace</span>
        </Link>
        <button 
          className="btn btn-primary btn-sm"
          onClick={() => window.print()}
        >
          <Download size={14} />
          <span>Export PDF</span>
        </button>
      </div>

      <div className="report-container">
        <article className="report-document">
          
          {/* ── Cover Page ── */}
          <header className="report-cover">
            <div className="cover-bg-glow"></div>
            <div className="cover-icon">
              <Sparkles size={32} />
            </div>
            <h1 className="cover-title">Intelligence Report</h1>
            <h2 className="cover-company">{report.company}</h2>
            <div className="cover-meta">
              {report.period && <span className="badge badge-neutral">Period: {report.period}</span>}
              <span className="badge badge-neutral">Generated: {new Date().toLocaleDateString()}</span>
            </div>
          </header>

          <div className="report-body">
            
            {/* ── Executive Summary ── */}
            {report.executive_summary && (
              <section className="report-section report-summary-callout">
                <h3 className="section-title">
                  <Sparkles size={18} className="text-primary" />
                  Executive Summary
                </h3>
                <div className="section-content text-lg font-medium leading-relaxed">
                  {report.executive_summary}
                </div>
              </section>
            )}

            {/* ── Company Overview ── */}
            <section className="report-section">
              <h3 className="section-title">
                <Building2 size={18} className="text-primary" />
                Company Overview
              </h3>
              <div className="report-grid">
                <div className="grid-cell">
                  <h4 className="cell-title">Business Model</h4>
                  <p>{report.business_model || report.company_overview}</p>
                </div>
                <div className="grid-cell">
                  <h4 className="cell-title">Products & Services</h4>
                  <p>{report.products_and_services}</p>
                </div>
                {report.market_presence && (
                  <div className="grid-cell full-width">
                    <h4 className="cell-title">Market Presence</h4>
                    <p>{report.market_presence}</p>
                  </div>
                )}
              </div>
            </section>

            {/* ── Financial Performance ── */}
            {(report.financial_performance || (report.financial_insights && report.financial_insights.length > 0)) && (
              <section className="report-section">
                <h3 className="section-title">
                  <DollarSign size={18} className="text-primary" />
                  Financial Performance
                </h3>
                
                {report.financial_performance && (
                  <p className="mb-6 leading-relaxed">{report.financial_performance}</p>
                )}
                
                {report.financial_insights && report.financial_insights.length > 0 && (
                  <div className="report-grid">
                    {report.financial_insights.map((insight, idx) => (
                      <div key={idx} className="metric-card">
                        <div className="metric-header">
                          <span className="metric-name">{insight.metric}</span>
                          <span className={`badge ${insight.change?.includes('-') ? 'badge-danger' : 'badge-success'}`}>
                            {insight.change || 'N/A'}
                          </span>
                        </div>
                        <div className="metric-values">
                          <div>
                            <span className="metric-val-label">Current</span>
                            <span className="metric-val-data font-bold">{insight.current_value}</span>
                          </div>
                          <div className="text-right">
                            <span className="metric-val-label">Previous</span>
                            <span className="metric-val-data text-muted">{insight.previous_value}</span>
                          </div>
                        </div>
                        <p className="metric-interpretation">{insight.interpretation}</p>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            )}

            {/* ── Key Risks ── */}
            {report.key_risks && report.key_risks.length > 0 && (
              <section className="report-section">
                <h3 className="section-title">
                  <AlertTriangle size={18} className="text-danger" />
                  Risk Intelligence
                </h3>
                
                <div className="space-y-4">
                  {report.key_risks.map((risk, idx) => {
                    const sevClass = risk.severity.toLowerCase();
                    return (
                      <div key={idx} className="risk-row">
                        <div className={`risk-indicator ${sevClass}`}></div>
                        <div className="risk-content">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-bold text-text-primary">{risk.risk}</h4>
                            <span className="badge badge-neutral text-[0.625rem]">{risk.category}</span>
                            <span className={`badge badge-${sevClass === 'critical' || sevClass === 'high' ? 'danger' : 'warning'} text-[0.625rem]`}>
                              {risk.severity}
                            </span>
                          </div>
                          <p className="text-sm text-text-secondary leading-relaxed">{risk.explanation}</p>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </section>
            )}

            {/* ── Indicators ── */}
            <div className="report-grid mb-10">
              {report.positive_indicators && report.positive_indicators.length > 0 && (
                <div className="indicator-panel positive">
                  <h4 className="flex items-center gap-2 font-bold text-success mb-3">
                    <TrendingUp size={16} /> Positive Indicators
                  </h4>
                  <ul className="indicator-list">
                    {report.positive_indicators.map((item, idx) => <li key={idx}>{item}</li>)}
                  </ul>
                </div>
              )}
              
              {report.warning_indicators && report.warning_indicators.length > 0 && (
                <div className="indicator-panel warning">
                  <h4 className="flex items-center gap-2 font-bold text-warning mb-3">
                    <AlertTriangle size={16} /> Warning Indicators
                  </h4>
                  <ul className="indicator-list">
                    {report.warning_indicators.map((item, idx) => <li key={idx}>{item}</li>)}
                  </ul>
                </div>
              )}
            </div>

            {/* ── Conclusion ── */}
            {report.overall_summary && (
              <section className="report-section conclusion-panel">
                <h3 className="section-title border-none mb-3">Conclusion</h3>
                <p className="font-medium text-[1.0625rem] leading-relaxed">
                  {report.overall_summary}
                </p>
              </section>
            )}
            
            {/* ── Footer ── */}
            <footer className="report-footer">
              <p><strong>Disclaimer:</strong> {report.disclaimer || 'This report is generated by AI and may contain inaccuracies. It does not constitute financial advice. Always verify with original source documents.'}</p>
              <div className="watermark">InvestiLens AI</div>
            </footer>

          </div>
        </article>
      </div>
    </div>
  );
};

export default ReportPage;
