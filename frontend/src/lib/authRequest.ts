import { clearTokens, getAccessToken, setTokens } from './api';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');

let refreshPromise: Promise<string | null> | null = null;

async function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;

  const refresh = localStorage.getItem('key_refresh_token');
  if (!refresh) return null;

  refreshPromise = (async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ refresh }),
      });
      if (!response.ok) return null;
      const data = (await response.json().catch(() => ({}))) as { access?: string; refresh?: string };
      if (!data.access) return null;
      setTokens(data.access, data.refresh);
      return data.access;
    } catch {
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

function errorMessage(status: number, text: string, fallback: string) {
  if (!text) return fallback;
  try {
    const parsed = JSON.parse(text) as Record<string, unknown>;
    if (typeof parsed.detail === 'string') return parsed.detail;
    return Object.entries(parsed)
      .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : String(value)}`)
      .join(' ');
  } catch {
    // Django/Vercel can return an HTML 500 page. Never expose that page to users.
    if (text.trimStart().toLowerCase().startsWith('<!doctype html') || text.includes('<html')) {
      return status >= 500
        ? 'The server could not complete this request. Please try again. If the problem continues, contact your school administrator.'
        : fallback;
    }
    return text;
  }
}

export async function authRequest<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  const token = getAccessToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });

  if (response.status === 401 && retry) {
    const refreshed = await refreshAccessToken();
    if (refreshed) return authRequest<T>(path, init, false);
    clearTokens();
    throw new Error('Your session has expired. Please sign in again.');
  }

  if (!response.ok) {
    const text = await response.text().catch(() => '');
    throw new Error(errorMessage(response.status, text, `Request failed (${response.status}).`));
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}
