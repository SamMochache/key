import { getAccessToken } from './api';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');

export type TimetableStatus = 'DRAFT' | 'PUBLISHED' | 'ARCHIVED';
export type WeekDay = 'MONDAY' | 'TUESDAY' | 'WEDNESDAY' | 'THURSDAY' | 'FRIDAY';

export interface ApiPeriod { id: string; school: string; school_name: string; name: string; sequence: number; start_time: string; end_time: string; is_break: boolean; }
export interface ApiTimetable { id: string; school: string; school_name: string; academic_year: string; academic_year_name: string; term: string; term_number: number; name: string; version: number; status: TimetableStatus; effective_from: string; effective_to: string | null; entry_count: number; }
export interface ApiTeacherSubject { id: string; teacher: string; teacher_name: string; subject: string; subject_name: string; classroom: string; classroom_name: string; academic_year: string; academic_year_name: string; term: string; term_number: number; role: string; start_date: string; end_date: string | null; is_active: boolean; }
export interface ApiTimetableEntry { id: string; timetable: string; weekday: WeekDay; period: string; period_name: string; start_time: string; end_time: string; is_break: boolean; classroom: string; classroom_name: string; teacher_subject: string; subject_name: string; teacher_name: string; room: string; }

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

async function list<T>(path: string) {
  const data = await request<Paginated<T> | T[]>(path);
  return Array.isArray(data) ? data : data.results;
}

export function listPeriods(school?: string) { return list<ApiPeriod>(`/periods/${school ? `?school=${encodeURIComponent(school)}` : ''}`); }
export function listTimetables(params: { academicYear?: string; term?: string; status?: string } = {}) {
  const query = new URLSearchParams();
  if (params.academicYear) query.set('academic_year', params.academicYear);
  if (params.term) query.set('term', params.term);
  if (params.status) query.set('status', params.status);
  return list<ApiTimetable>(`/timetables/${query.toString() ? `?${query}` : ''}`);
}
export function listTeacherSubjects(params: { classroom?: string; academicYear?: string; term?: string; active?: boolean } = {}) {
  const query = new URLSearchParams();
  if (params.classroom) query.set('classroom', params.classroom);
  if (params.academicYear) query.set('academic_year', params.academicYear);
  if (params.term) query.set('term', params.term);
  if (params.active) query.set('active', 'true');
  return list<ApiTeacherSubject>(`/teacher-subjects/${query.toString() ? `?${query}` : ''}`);
}
export function listTimetableEntries(params: { timetable?: string; classroom?: string; published?: boolean } = {}) {
  const query = new URLSearchParams();
  if (params.timetable) query.set('timetable', params.timetable);
  if (params.classroom) query.set('classroom', params.classroom);
  if (params.published) query.set('published', 'true');
  return list<ApiTimetableEntry>(`/timetable-entries/${query.toString() ? `?${query}` : ''}`);
}
export function createPeriod(payload: Record<string, unknown>) { return request<ApiPeriod>('/periods/', { method: 'POST', body: JSON.stringify(payload) }); }
export function updatePeriod(id: string, payload: Record<string, unknown>) { return request<ApiPeriod>(`/periods/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) }); }
export function createTimetable(payload: Record<string, unknown>) { return request<ApiTimetable>('/timetables/', { method: 'POST', body: JSON.stringify(payload) }); }
export function updateTimetable(id: string, payload: Record<string, unknown>) { return request<ApiTimetable>(`/timetables/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) }); }
export function publishTimetable(id: string) { return request<ApiTimetable>(`/timetables/${id}/publish/`, { method: 'POST' }); }
export function archiveTimetable(id: string) { return request<ApiTimetable>(`/timetables/${id}/archive/`, { method: 'POST' }); }
export function createTimetableVersion(id: string) { return request<ApiTimetable>(`/timetables/${id}/new-version/`, { method: 'POST' }); }
export function createTimetableEntry(payload: Record<string, unknown>) { return request<ApiTimetableEntry>('/timetable-entries/', { method: 'POST', body: JSON.stringify(payload) }); }
export function updateTimetableEntry(id: string, payload: Record<string, unknown>) { return request<ApiTimetableEntry>(`/timetable-entries/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) }); }
export function deleteTimetableEntry(id: string) { return request<void>(`/timetable-entries/${id}/`, { method: 'DELETE' }); }
