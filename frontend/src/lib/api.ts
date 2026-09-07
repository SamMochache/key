const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');

const ACCESS_TOKEN_KEY = 'key_access_token';
const REFRESH_TOKEN_KEY = 'key_refresh_token';

export interface ApiAssessment {
  id: string;
  lesson_session: string;
  lesson_session_title: string;
  teacher: string;
  teacher_name: string;
  title: string;
  description: string;
  assessment_type: string;
  status: string;
  due_date: string | null;
  maximum_score: string | null;
  allow_resubmission: boolean;
  rubric?: ApiRubric | null;
}

export interface ApiRubric {
  id: string;
  title: string;
  description: string;
  criteria: ApiRubricCriterion[];
}

export interface ApiRubricCriterion {
  id: string;
  title: string;
  description: string;
  maximum_score: string;
  sequence: number;
}

export interface ApiSubmission {
  id: string;
  assessment: string;
  enrollment: string;
  student_name: string;
  admission_number: string;
  status: string;
  submitted_at: string | null;
}

export interface DashboardSummary {
  students: number;
  assessments: number;
  submissions: number;
  evaluations: number;
  published_evaluations: number;
  upcoming_assessments: number;
}

interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface CurrentUser {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  initials: string;
  phone_number: string;
  preferred_language: string;
  timezone: string;
  status: string;
  role: string;
  school_id?: string;
}

interface TokenPair {
  access: string;
  refresh: string;
}

export function getAccessToken(): string | null {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
}

export function setTokens(access: string, refresh?: string) {
  localStorage.setItem(ACCESS_TOKEN_KEY, access);
  if (refresh) localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export async function login(username: string, password: string): Promise<CurrentUser> {
  const response = await fetch(`${API_BASE_URL}/auth/token/`, {
    method: 'POST',
    headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    throw new Error(detail || 'Unable to sign in.');
  }

  const tokens = await response.json() as TokenPair;
  setTokens(tokens.access, tokens.refresh);
  return getCurrentUser();
}

async function refreshAccessToken(): Promise<string | null> {
  const refresh = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!refresh) return null;

  const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
    method: 'POST',
    headers: { 'Accept': 'application/json', 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh })
  });

  if (!response.ok) {
    clearTokens();
    return null;
  }

  const data = await response.json() as { access: string; refresh?: string };
  setTokens(data.access, data.refresh);
  return data.access;
}

async function request<T>(path: string, init: RequestInit = {}, retry = true): Promise<T> {
  const token = getAccessToken();
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');

  if (init.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  if (token) headers.set('Authorization', `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });

  if (response.status === 401 && retry) {
    const refreshed = await refreshAccessToken();
    if (refreshed) return request<T>(path, init, false);
  }

  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    throw new Error(detail || `API request failed (${response.status})`);
  }

  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function getCurrentUser() {
  return request<CurrentUser>('/auth/me/');
}

export async function listAssessments() {
  const data = await request<Paginated<ApiAssessment> | ApiAssessment[]>('/assessments/');
  return Array.isArray(data) ? data : data.results;
}

export async function listSubmissions() {
  const data = await request<Paginated<ApiSubmission> | ApiSubmission[]>('/submissions/');
  return Array.isArray(data) ? data : data.results;
}

export async function getDashboardSummary() {
  const data = await request<DashboardSummary | Paginated<DashboardSummary> | DashboardSummary[]>('/dashboard-summary/');
  if (Array.isArray(data)) return data[0];
  if ('results' in data) return data.results[0];
  return data;
}

export { API_BASE_URL };
