import { API_BASE_URL, getAccessToken } from './api';

export type PortfolioItemType = 'PROJECT' | 'ARTWORK' | 'PHOTO' | 'VIDEO' | 'AUDIO' | 'CERTIFICATE' | 'OBSERVATION' | 'PRESENTATION' | 'ASSESSMENT' | 'OTHER';

export interface ApiArtifact {
  id: string;
  portfolio_item: string;
  file: string;
  file_url: string | null;
  caption: string;
  created_at: string;
  updated_at: string;
}

export interface ApiPortfolioItem {
  id: string;
  portfolio: string;
  student_name: string;
  lesson_session: string | null;
  assessment_submission: string | null;
  assessment_title: string | null;
  item_type: PortfolioItemType;
  item_type_label: string;
  title: string;
  description: string;
  event_date: string;
  artifacts: ApiArtifact[];
  created_at: string;
  updated_at: string;
}

export interface ApiPortfolio {
  id: string;
  student: string;
  student_name: string;
  admission_number: string;
  summary: string;
  item_count: number;
  created_at: string;
  updated_at: string;
}

interface Paginated<T> { count: number; next: string | null; previous: string | null; results: T[]; }

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  const token = getAccessToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (init.body && !(init.body instanceof FormData) && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    let message = detail;
    try {
      const parsed = JSON.parse(detail);
      message = Object.entries(parsed).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : String(value)}`).join(' ');
    } catch {}
    throw new Error(message || `Portfolio request failed (${response.status})`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function getMyPortfolio() { return request<ApiPortfolio>('/portfolios/mine/'); }
export async function listPortfolios() { const data = await request<Paginated<ApiPortfolio> | ApiPortfolio[]>('/portfolios/'); return Array.isArray(data) ? data : data.results; }
export async function updatePortfolio(id: string, summary: string) { return request<ApiPortfolio>(`/portfolios/${id}/`, { method: 'PATCH', body: JSON.stringify({ summary }) }); }
export async function listPortfolioItems(params: { portfolio?: string; itemType?: PortfolioItemType; search?: string } = {}) {
  const query = new URLSearchParams();
  if (params.portfolio) query.set('portfolio', params.portfolio);
  if (params.itemType) query.set('item_type', params.itemType);
  if (params.search) query.set('search', params.search);
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const data = await request<Paginated<ApiPortfolioItem> | ApiPortfolioItem[]>(`/portfolio-items/${suffix}`);
  return Array.isArray(data) ? data : data.results;
}
export async function createPortfolioItem(payload: { portfolio: string; item_type: PortfolioItemType; title: string; description?: string; event_date: string; assessment_submission?: string | null; lesson_session?: string | null }) {
  return request<ApiPortfolioItem>('/portfolio-items/', { method: 'POST', body: JSON.stringify(payload) });
}
export async function updatePortfolioItem(id: string, payload: Partial<{ item_type: PortfolioItemType; title: string; description: string; event_date: string; assessment_submission: string | null; lesson_session: string | null }>) {
  return request<ApiPortfolioItem>(`/portfolio-items/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
}
export async function deletePortfolioItem(id: string) { return request<void>(`/portfolio-items/${id}/`, { method: 'DELETE' }); }
export async function createPortfolioArtifact(portfolioItem: string, file: File, caption = '') {
  const body = new FormData(); body.append('portfolio_item', portfolioItem); body.append('file', file); body.append('caption', caption);
  return request<ApiArtifact>('/portfolio-artifacts/', { method: 'POST', body });
}
