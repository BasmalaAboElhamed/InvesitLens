import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Layers, LayoutGrid, BarChart3, FileBarChart, Settings, AlertTriangle, Loader2 } from 'lucide-react';
import { systemService } from '../services/api';
import './Navbar.css';

const Navbar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);
  const [showResetModal, setShowResetModal] = useState(false);
  const [isResetting, setIsResetting] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const isActive = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  const handleReset = async () => {
    if (isResetting) return;
    setIsResetting(true);
    try {
      await systemService.resetAllData();
      // Clear all local storage/session storage related to the app if any
      localStorage.clear();
      sessionStorage.clear();
      
      // Close modal
      setShowResetModal(false);
      
      // Force reload to clear all React state and start fresh
      window.location.href = '/';
    } catch (error) {
      console.error("Failed to reset data", error);
      alert("Failed to reset data. See console for details.");
      setIsResetting(false);
    }
  };

  return (
    <header className={`navbar${scrolled ? ' navbar-scrolled' : ''}`} role="banner">
      <div className="navbar-inner">
        {/* Brand */}
        <Link to="/" className="navbar-brand" aria-label="InvestiLens home">
          <div className="brand-icon" aria-hidden="true">
            <Layers size={18} strokeWidth={2.5} />
          </div>
          <span className="brand-name">InvestiLens</span>
          <span className="brand-tag">AI</span>
        </Link>

        {/* Navigation */}
        <nav className="navbar-links" aria-label="Main navigation">
          <Link
            to="/"
            id="nav-workspaces"
            className={`nav-link${isActive('/') && !location.pathname.includes('/company') ? ' active' : ''}`}
          >
            <LayoutGrid size={15} strokeWidth={2} />
            <span>Workspaces</span>
          </Link>
          <Link
            to="/analysis"
            id="nav-analysis"
            className={`nav-link${isActive('/analysis') ? ' active' : ''}`}
          >
            <BarChart3 size={15} strokeWidth={2} />
            <span>Analysis</span>
          </Link>
          <Link
            to="/reports"
            id="nav-reports"
            className={`nav-link${isActive('/reports') ? ' active' : ''}`}
          >
            <FileBarChart size={15} strokeWidth={2} />
            <span>Reports</span>
          </Link>
        </nav>

        {/* Status pill & Settings */}
        <div className="navbar-actions" style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="navbar-status" aria-label="System status: Operational">
            <span className="status-dot" aria-hidden="true" />
            <span>Operational</span>
          </div>
          
          <button 
            className="btn btn-ghost btn-icon" 
            style={{ color: 'var(--text-muted)' }}
            onClick={() => setShowResetModal(true)}
            aria-label="Settings / Reset Data"
            title="Developer Settings"
          >
            <Settings size={18} />
          </button>
        </div>
      </div>

      {/* Reset Modal */}
      {showResetModal && (
        <div className="modal-overlay" style={{ zIndex: 1000 }}>
          <div className="modal-content card card-glass" style={{ borderTop: '4px solid var(--danger)' }}>
            <div className="modal-header">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-danger-soft text-danger flex items-center justify-center">
                  <AlertTriangle size={20} />
                </div>
                <div>
                  <h2 className="text-xl font-bold text-text-primary">Reset InvestiLens?</h2>
                </div>
              </div>
            </div>
            
            <div className="py-4">
              <p className="text-text-secondary mb-4">
                This will permanently delete all user data and return the application to a fresh installation state.
              </p>
              
              <ul className="text-sm text-text-muted space-y-2 mb-6 ml-1">
                <li className="flex items-center gap-2">• Uploaded documents & PDFs</li>
                <li className="flex items-center gap-2">• Companies & Workspaces</li>
                <li className="flex items-center gap-2">• Analyses & Reports</li>
                <li className="flex items-center gap-2">• History & Chat data</li>
                <li className="flex items-center gap-2">• Local application data</li>
              </ul>
              
              <p className="text-sm font-bold text-danger">This action cannot be undone.</p>
            </div>
            
            <div className="modal-actions mt-2">
              <button 
                className="btn btn-secondary" 
                onClick={() => setShowResetModal(false)}
                disabled={isResetting}
              >
                Cancel
              </button>
              <button 
                className="btn btn-danger" 
                onClick={handleReset}
                disabled={isResetting}
              >
                {isResetting ? (
                  <>
                    <Loader2 size={16} className="animate-spin" />
                    <span>Resetting...</span>
                  </>
                ) : (
                  <>
                    <AlertTriangle size={16} />
                    <span>Reset Everything</span>
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
