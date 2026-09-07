import { getAccessToken } from './api';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');

export interface ParentStudentLink {
  id: string;
  name: string;
  admission_number: string;
  relationship: string;
  can_view_reports: boolean;
  is_primary_contact: boolean;
}

export interface ApiParent {
  id: string;
  user: string;
  full_name: string;
  email: string;
  phone_number: string;
  school: string;
  school_name: string;
  is_active: boolean;
  students: ParentStudentLink[];
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
      ...(options.headers || {}),
    },
  });
  const text = await response.text().catch(() => '');
  let payload: any = {};
  try { payload = text ? JSON.parse(text) : {}; } catch { /* handled below */ }
  if (!response.ok) throw new Error(payload.detail || `Request failed (${response.status}).`);
  return payload as T;
}

export async function listParents(search?: string) {
  const suffix = search?.trim() ? `?search=${encodeURIComponent(search.trim())}` : '';
  return request<{ results: ApiParent[] }>(`/parents/${suffix}`);
}

export async function createParent(payload: {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  phone_number?: string;
  school: string;
  student: string;
  relationship?: string;
  can_view_reports?: boolean;
  is_primary_contact?: boolean;
}) {
  return request<ApiParent & { student: ParentStudentLink }>('/parents/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateParent(id: string, payload: Record<string, unknown>) {
  return request<{ id: string; full_name: string; is_active: boolean }>('/parents/', {
    method: 'PATCH',
    body: JSON.stringify({ id, ...payload }),
  });
}
