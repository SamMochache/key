import { getAccessToken } from './api';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');

export type CalendarEventType = 'ACADEMIC' | 'HOLIDAY' | 'EXAMINATION' | 'MEETING' | 'ACTIVITY' | 'DEADLINE' | 'OTHER';
export interface ApiCalendarEvent { id: string; school: string; school_name: string; academic_year: string; academic_year_name: string; term: string | null; term_number: number | null; title: string; event_type: CalendarEventType; start_at: string; end_at: string; all_day: boolean; location: string; description: string; is_active: boolean; }
interface Paginated<T> { results: T[]; count: number; }

async function request<T>(path: string, init: RequestInit = {}) {
  const token = getAccessToken();
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  const text = await response.text();
  let data: any = {};
  try { data = text ? JSON.parse(text) : {}; } catch { /* handled below */ }
  if (!response.ok) {
    const message = data?.detail || Object.entries(data).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : String(value)}`).join(' ') || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return data as T;
}

export async function listCalendarEvents(params: { academicYear?: string; term?: string; start?: string; end?: string; eventType?: CalendarEventType; search?: string } = {}) {
  const query = new URLSearchParams();
  if (params.academicYear) query.set('academic_year', params.academicYear);
  if (params.term) query.set('term', params.term);
  if (params.start) query.set('start', params.start);
  if (params.end) query.set('end', params.end);
  if (params.eventType) query.set('event_type', params.eventType);
  if (params.search) query.set('search', params.search);
  const data = await request<Paginated<ApiCalendarEvent> | ApiCalendarEvent[]>(`/calendar-events/${query.toString() ? `?${query}` : ''}`);
  return Array.isArray(data) ? data : data.results;
}

export function createCalendarEvent(payload: Record<string, unknown>) { return request<ApiCalendarEvent>('/calendar-events/', { method: 'POST', body: JSON.stringify(payload) }); }
export function updateCalendarEvent(id: string, payload: Record<string, unknown>) { return request<ApiCalendarEvent>(`/calendar-events/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) }); }
export function deleteCalendarEvent(id: string) { return request<void>(`/calendar-events/${id}/`, { method: 'DELETE' }); }
