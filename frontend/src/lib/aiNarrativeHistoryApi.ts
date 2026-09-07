import { getAccessToken } from './api';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');

export interface AINarrativeHistoryItem {
  id: string;
  action: 'GENERATED' | 'EDITED' | 'REVIEWED' | 'PUBLISHED';
  status: 'DRAFT' | 'REVIEWED' | 'PUBLISHED';
  actor: { id: string; name: string };
  occurred_at: string;
  model: string;
  narrative: Record<string, string>;
  source_data: Record<string, unknown>;
  metadata: Record<string, unknown>;
}

export async function listAINarrativeReportHistory(reportId: string) {
  const response = await fetch(`${API_BASE_URL}/reports/ai-narrative/history/?report=${encodeURIComponent(reportId)}`, {
    headers: {
      Accept: 'application/json',
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
    },
  });
  const detail = await response.text().catch(() => '');
  let payload: any = {};
  try { payload = detail ? JSON.parse(detail) : {}; } catch { /* handled below */ }
  if (!response.ok) throw new Error(payload.detail || `Unable to load report history (${response.status}).`);
  return payload as { results: AINarrativeHistoryItem[] };
}
