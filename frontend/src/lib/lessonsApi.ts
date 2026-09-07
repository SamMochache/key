import { API_BASE_URL, getAccessToken } from './api';

export type LessonStatus = 'SCHEDULED' | 'IN_PROGRESS' | 'COMPLETED' | 'CANCELLED' | 'MISSED';

export interface ApiLesson {
  id: string;
  timetable_entry: string;
  classroom: string;
  classroom_name: string;
  subject: string;
  subject_name: string;
  teacher: string;
  teacher_name: string;
  term: string;
  term_number: number;
  weekday: string;
  start_time: string;
  end_time: string;
  room: string;
  lesson_date: string;
  started_at: string | null;
  ended_at: string | null;
  status: LessonStatus;
  remarks: string;
  created_at: string;
  updated_at: string;
}

interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

interface SyncDayResponse {
  created: number;
  lesson_date: string;
  lessons: ApiLesson[];
}

async function lessonRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getAccessToken();
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    let message = detail;
    try {
      const parsed = JSON.parse(detail);
      message = Object.entries(parsed)
        .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : String(value)}`)
        .join(' ');
    } catch {}
    throw new Error(message || `Lessons API request failed (${response.status})`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function listLessons(params: { lessonDate?: string; status?: LessonStatus; search?: string } = {}) {
  const query = new URLSearchParams();
  if (params.lessonDate) query.set('lesson_date', params.lessonDate);
  if (params.status) query.set('status', params.status);
  if (params.search?.trim()) query.set('search', params.search.trim());
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const data = await lessonRequest<Paginated<ApiLesson> | ApiLesson[]>(`/lessons/${suffix}`);
  return Array.isArray(data) ? data : data.results;
}

export async function syncLessonDay(lessonDate: string) {
  return lessonRequest<SyncDayResponse>('/lessons/sync-day/', {
    method: 'POST',
    body: JSON.stringify({ lesson_date: lessonDate })
  });
}

export async function startLesson(id: string) {
  return lessonRequest<ApiLesson>(`/lessons/${id}/start/`, { method: 'POST' });
}

export async function completeLesson(id: string, remarks = '') {
  return lessonRequest<ApiLesson>(`/lessons/${id}/complete/`, {
    method: 'POST',
    body: JSON.stringify({ remarks })
  });
}
