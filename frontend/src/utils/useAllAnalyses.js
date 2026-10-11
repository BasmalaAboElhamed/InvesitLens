import { useCallback, useEffect, useRef, useState } from 'react';
import { companyService, analysisService } from '../services/api';

// Statuses that mean "the pipeline is still working".
const IN_PROGRESS_STATUSES = ['uploading', 'processing', 'indexing', 'analyzing'];

export const isInProgress = (status) => IN_PROGRESS_STATUSES.includes(status);

/**
 * The backend stores times as naive UTC (no "Z" suffix), which browsers would
 * read as local time. Add the "Z" so dates show correctly in the user's timezone.
 */
export const parseServerDate = (value) => {
  if (!value) return null;
  const hasTimezone = /([zZ]|[+-]\d{2}:?\d{2})$/.test(value);
  return new Date(hasTimezone ? value : `${value}Z`);
};

export const formatDateTime = (value) => {
  const date = parseServerDate(value);
  if (!date || Number.isNaN(date.getTime())) return '—';
  return date.toLocaleString(undefined, {
    year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit',
  });
};

export const formatDuration = (start, end) => {
  const from = parseServerDate(start);
  const to = parseServerDate(end);
  if (!from || !to) return null;
  const seconds = Math.max(0, Math.round((to - from) / 1000));
  if (seconds < 60) return `${seconds}s`;
  return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
};

/**
 * Loads every analysis run of every company (newest first).
 * Each run also gets `company` ({ id, name, ticker, industry }) for display.
 *
 * @param {number} pollMs  When > 0, refreshes silently every `pollMs` milliseconds
 *                         while at least one run is still in progress.
 */
export default function useAllAnalyses({ pollMs = 0 } = {}) {
  const [runs, setRuns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const mounted = useRef(true);

  const load = useCallback(async ({ silent = false } = {}) => {
    try {
      if (!silent) setLoading(true);
      const companies = await companyService.getCompanies();
      const perCompany = await Promise.all(
        companies.map(async (company) => {
          const analyses = await analysisService.getCompanyAnalyses(company.id);
          return analyses.map((analysis) => ({ ...analysis, company }));
        })
      );
      if (!mounted.current) return;
      const all = perCompany.flat().sort(
        (a, b) => parseServerDate(b.started_at) - parseServerDate(a.started_at)
      );
      setRuns(all);
      setError(null);
    } catch (err) {
      console.error('Failed to load analyses', err);
      if (mounted.current) setError(err);
    } finally {
      if (mounted.current && !silent) setLoading(false);
    }
  }, []);

  useEffect(() => {
    mounted.current = true;
    load();
    return () => { mounted.current = false; };
  }, [load]);

  const hasRunning = runs.some((run) => isInProgress(run.status));
  useEffect(() => {
    if (!pollMs || !hasRunning) return undefined;
    const timer = setTimeout(() => load({ silent: true }), pollMs);
    return () => clearTimeout(timer);
  }, [pollMs, hasRunning, runs, load]);

  return { runs, loading, error, reload: load };
}
