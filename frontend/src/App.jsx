import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import CompanyWorkspace from './pages/CompanyWorkspace';
import ReportPage from './pages/ReportPage';
import AnalysisPage from './pages/AnalysisPage';
import ReportsPage from './pages/ReportsPage';

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/company/:companyId/*" element={<CompanyWorkspace />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/reports" element={<ReportsPage />} />
            <Route path="/report/:analysisId" element={<ReportPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
