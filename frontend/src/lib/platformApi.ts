import { getAccessToken } from './api';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');

export interface PlatformSummary {
  institutions: number;
  active_institutions: number;
  students: number;
  teachers: number;
  parents: number;
  users: number;
  ai_reports: number;
}

export interface PlatformUser {
  id: string;
  full_name: string;
  email: string;
  role: 'platform_admin' | 'admin' | 'teacher' | 'student' | 'parent' | 'user';
  school_id: string | null;
  school_name: string | null;
  is_active: boolean;
  status: string;
  last_login: string | null;
  created_at: string;
}

export interface PlatformAuditLog {
  id: string;
  action: string;
  resource_type: string;
  resource_id: string;
  actor: string;
  actor_email: string | null;
  school: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface PlatformSchool {
  id: string;
  name: string;
  short_name: string;
  email: string;
  phone_number: string;
  address: string;
  city: string;
  country: string;
  timezone: string;
  website?: string;
  logo: string | null;
  is_active: boolean;
  student_count?: number;
  teacher_count?: number;
  created_at: string;
  updated_at: string;
}

export interface InstitutionOverview {
  school: PlatformSchool;
  users: PlatformUser[];
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

async function platformRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getAccessToken();
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers, cache: 'no-store' });
  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    let message = detail;
    try {
      const parsed = JSON.parse(detail);
      message = parsed.detail || Object.values(parsed).flat().join(' ');
    } catch {}
    throw new Error(message || `Platform API request failed (${response.status})`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export const getPlatformSummary = () => platformRequest<PlatformSummary>('/platform/summary/');

export async function listPlatformUsers(params: { search?: string; role?: string; school?: string; active?: string } = {}) {
  const query = new URLSearchParams();
  if (params.search?.trim()) query.set('search', params.search.trim());
  if (params.role) query.set('role', params.role);
  if (params.school) query.set('school', params.school);
  if (params.active) query.set('active', params.active);
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return platformRequest<Paginated<PlatformUser>>(`/platform/users/${suffix}`);
}

export function setPlatformUserStatus(id: string, isActive: boolean) {
  return platformRequest<PlatformUser>(`/platform/users/${id}/status/`, {
    method: 'PATCH',
    body: JSON.stringify({ is_active: isActive }),
  });
}

export async function listPlatformAuditLogs(params: { action?: string } = {}) {
  const suffix = params.action ? `?action=${encodeURIComponent(params.action)}` : '';
  return platformRequest<Paginated<PlatformAuditLog>>(`/platform/audit-logs/${suffix}`);
}

export const getPlatformSettings = () => platformRequest<Record<string, string>>('/platform/settings/');

export const updatePlatformSettings = (payload: Record<string, string>) =>
  platformRequest<Record<string, string>>('/platform/settings/', {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });

export const getInstitutionOverview = (id: string) =>
  platformRequest<InstitutionOverview>(`/platform/institutions/${id}/`);

export const createSchoolAdministrator = (
  schoolId: string,
  payload: { email: string; first_name: string; last_name: string; password: string; phone_number?: string },
) => platformRequest<PlatformUser>(`/platform/institutions/${schoolId}/administrators/`, {
  method: 'POST',
  body: JSON.stringify(payload),
});

export const updateInstitution = (id: string, payload: Partial<PlatformSchool>) =>
  platformRequest<PlatformSchool>(`/schools/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });

export const createInstitution = (payload: Partial<PlatformSchool>) =>
  platformRequest<PlatformSchool>('/schools/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
