import React, { useState, useRef } from 'react';
import { Upload, FileText, Trash2, CheckCircle2, Clock, AlertCircle, Loader2 } from 'lucide-react';
import { documentService } from '../services/api';

const DocumentsManager = ({ company, documents, onDocumentUploaded }) => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (file.type !== 'application/pdf') {
      alert('Only PDF files are supported');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('company_id', company.id);
    formData.append('document_name', file.name.replace('.pdf', ''));
    
    // Auto-detect year if in filename (e.g., 2023_annual_report.pdf)
    const yearMatch = file.name.match(/20\d{2}/);
    if (yearMatch) {
      formData.append('year', yearMatch[0]);
    }

    try {
      setUploading(true);
      setUploadProgress(20);
      
      await documentService.uploadDocument(formData);
      setUploadProgress(100);
      
      if (fileInputRef.current) fileInputRef.current.value = '';
      
      setTimeout(() => {
        onDocumentUploaded();
        setUploading(false);
        setUploadProgress(0);
      }, 800);
      
    } catch (error) {
      console.error("Upload failed", error);
      alert("Upload failed. Check console for details.");
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'indexed':
        return (
          <span className="badge badge-success">
            <CheckCircle2 size={12} /> Indexed
          </span>
        );
      case 'processing':
        return (
          <span className="badge badge-warning">
            <Clock size={12} className="animate-pulse" /> Processing
          </span>
        );
      case 'failed':
        return (
          <span className="badge badge-danger">
            <AlertCircle size={12} /> Failed
          </span>
        );
      default:
        return (
          <span className="badge badge-neutral">
            <Clock size={12} /> {status}
          </span>
        );
    }
  };

  return (
    <div className="module-container animate-in">
      <header className="module-header flex justify-between items-start flex-wrap gap-4">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-gradient-subtle">Document Library</h2>
          <p className="text-muted mt-1">Upload and manage financial reports for analysis</p>
        </div>
        
        <div>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            accept=".pdf" 
            className="hidden" 
            id="file-upload"
            aria-label="Upload PDF document"
          />
          <label 
            htmlFor="file-upload" 
            className={`btn ${uploading ? 'btn-secondary' : 'btn-primary'} cursor-pointer`}
          >
            {uploading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                <span>Uploading...</span>
              </>
            ) : (
              <>
                <Upload size={16} strokeWidth={2.5} />
                <span>Upload PDF</span>
              </>
            )}
          </label>
        </div>
      </header>

      {uploading && (
        <div className="card card-glass mb-6 p-5 border-primary animate-in" role="status">
          <div className="flex justify-between items-center mb-3">
            <span className="font-semibold text-primary flex items-center gap-2">
              <Loader2 size={16} className="animate-spin" />
              Processing document...
            </span>
            <span className="text-sm font-bold">{uploadProgress}%</span>
          </div>
          <div className="w-full bg-slate-800 rounded-full h-1.5 overflow-hidden">
            <div 
              className="bg-primary h-full rounded-full transition-all duration-300 ease-out" 
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {documents.length === 0 ? (
        <div className="empty-state card card-glass mt-2">
          <div className="empty-state-icon" aria-hidden="true">
            <FileText size={32} />
          </div>
          <h3 className="text-xl font-bold mt-2">No documents uploaded</h3>
          <p className="text-muted mt-2 max-w-md mx-auto">
            Upload annual reports, earnings call transcripts, or financial statements to begin AI analysis.
          </p>
          <button 
            className="btn btn-primary mt-6" 
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={16} strokeWidth={2.5} />
            <span>Upload First Document</span>
          </button>
        </div>
      ) : (
        <div className="grid gap-3" role="list" aria-label="Uploaded documents">
          {documents.map((doc, i) => (
            <article 
              key={doc.id} 
              className="card card-glass flex flex-col sm:flex-row sm:items-center justify-between p-4 gap-4 animate-in"
              style={{ animationDelay: `${i * 0.05}s` }}
              role="listitem"
            >
              <div className="flex items-start sm:items-center gap-4 min-w-0">
                <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center text-primary flex-shrink-0 border border-border">
                  <FileText size={20} />
                </div>
                <div className="min-w-0">
                  <h4 className="font-semibold text-[0.9375rem] truncate text-text-primary" title={doc.document_name}>
                    {doc.document_name}
                  </h4>
                  <div className="flex items-center flex-wrap gap-2 mt-1.5">
                    {doc.year && (
                      <span className="text-xs font-medium text-muted bg-slate-800/50 px-2 py-0.5 rounded">
                        FY {doc.year}
                      </span>
                    )}
                    {getStatusBadge(doc.status)}
                    {doc.status === 'indexed' && (
                      <span className="text-xs text-muted flex items-center gap-1.5">
                        <span className="w-1 h-1 rounded-full bg-border"></span>
                        {doc.page_count} pages
                        <span className="w-1 h-1 rounded-full bg-border"></span>
                        {doc.chunk_count} chunks
                      </span>
                    )}
                  </div>
                </div>
              </div>
              
              <button 
                className="btn btn-ghost btn-icon text-muted hover:text-danger hover:bg-danger-soft sm:self-center self-end"
                aria-label={`Delete ${doc.document_name}`}
                title="Delete document"
              >
                <Trash2 size={16} />
              </button>
            </article>
          ))}
        </div>
      )}
    </div>
  );
};

export default DocumentsManager;
