import { getAccessToken, setTokens } from './api';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');

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

async function request<T>(path: string, init: RequestInit = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      Authorization: `Bearer ${getAccessToken() || ''}`,
      ...(init.headers || {}),
    },
  });
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
