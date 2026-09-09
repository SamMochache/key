import { getAccessToken, setTokens } from './api';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');
const REFRESH_TOKEN_KEY = 'key_refresh_token';

export interface SelfProfile {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  initials: string;
  profile_photo?: string | null;
  phone_number: string;
  preferred_language: string;
  timezone: string;
  status: string;
  role: string;
  school_id?: string;
}

async function refreshAccessToken() {
  const refresh = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!refresh) return null;
  const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ refresh }),
  });
  if (!response.ok) return null;
  const data = await response.json().catch(() => ({}));
  if (!data.access) return null;
  setTokens(data.access, data.refresh);
  return data.access;
}

async function request<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const token = getAccessToken();
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init.headers || {}),
    },
  });

  if (response.status === 401 && retry) {
    const refreshed = await refreshAccessToken();
    if (refreshed) return request<T>(path, init, false);
  }

  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    let message = detail;
    try {
      const parsed = JSON.parse(detail);
      message = Object.entries(parsed).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : String(value)}`).join(' ');
    } catch {}
    throw new Error(message || `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const getMyProfile = () => request<SelfProfile>('/auth/me/');
export const updateMyProfile = (payload: Partial<Pick<SelfProfile, 'first_name' | 'last_name' | 'phone_number' | 'preferred_language' | 'timezone'>>) => request<SelfProfile>('/auth/me/', { method: 'PATCH', body: JSON.stringify(payload) });
export const changeMyPassword = (payload: { current_password: string; new_password: string; confirm_password: string }) => request<{ detail: string }>('/auth/change-password/', { method: 'POST', body: JSON.stringify(payload) });
