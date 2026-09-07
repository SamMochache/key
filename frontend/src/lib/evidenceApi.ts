import { API_BASE_URL, getAccessToken } from './api';

export type EvidenceType = 'DOCUMENT' | 'IMAGE' | 'VIDEO' | 'LINK' | 'OBSERVATION' | 'OTHER';

export interface ApiEvidence {
  id: string;
  submission: string;
  student_name: string;
  assessment_title: string;
  competency: string | null;
  competency_name: string | null;
  title: string;
  description: string;
  evidence_type: EvidenceType;
  file: string | null;
  file_url: string | null;
  url: string;
  created_by: string;
  created_by_name: string;
  created_at: string;
  updated_at: string;
}

interface Paginated<T> { count: number; next: string | null; previous: string | null; results: T[]; }

async function requestEvidence<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  const token = getAccessToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    let message = detail;
    try {
      const parsed = JSON.parse(detail);
      message = Object.entries(parsed).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : String(value)}`).join(' ');
    } catch {}
    throw new Error(message || `Evidence request failed (${response.status})`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function listEvidence(params: { submission?: string; competency?: string; evidenceType?: EvidenceType } = {}) {
  const query = new URLSearchParams();
  if (params.submission) query.set('submission', params.submission);
  if (params.competency) query.set('competency', params.competency);
  if (params.evidenceType) query.set('evidence_type', params.evidenceType);
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const data = await requestEvidence<Paginated<ApiEvidence> | ApiEvidence[]>(`/evidence/${suffix}`);
  return Array.isArray(data) ? data : data.results;
}

export async function createEvidence(payload: {
  submission: string;
  competency?: string | null;
  title: string;
  description?: string;
  evidence_type: EvidenceType;
  url?: string;
  file?: File | null;
}) {
  const body = new FormData();
  body.append('submission', payload.submission);
  if (payload.competency) body.append('competency', payload.competency);
  body.append('title', payload.title);
  body.append('description', payload.description || '');
  body.append('evidence_type', payload.evidence_type);
  if (payload.url) body.append('url', payload.url);
  if (payload.file) body.append('file', payload.file);
  return requestEvidence<ApiEvidence>('/evidence/', { method: 'POST', body });
}

export async function updateEvidence(id: string, payload: Partial<{
  competency: string | null;
  title: string;
  description: string;
  evidence_type: EvidenceType;
  url: string;
}>) {
  return requestEvidence<ApiEvidence>(`/evidence/${id}/`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
}
