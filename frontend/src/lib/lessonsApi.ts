import { authRequest } from './authRequest';

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

export async function listLessons(params: { lessonDate?: string; status?: LessonStatus; search?: string } = {}) {
  const query = new URLSearchParams();
  if (params.lessonDate) query.set('lesson_date', params.lessonDate);
  if (params.status) query.set('status', params.status);
  if (params.search?.trim()) query.set('search', params.search.trim());
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const data = await authRequest<Paginated<ApiLesson> | ApiLesson[]>(`/lessons/${suffix}`);
  return Array.isArray(data) ? data : data.results;
}

export async function syncLessonDay(lessonDate: string) {
  return authRequest<SyncDayResponse>('/lessons/sync-day/', {
    method: 'POST',
    body: JSON.stringify({ lesson_date: lessonDate })
  });
}

export async function startLesson(id: string) {
  return authRequest<ApiLesson>(`/lessons/${id}/start/`, { method: 'POST' });
}

export async function completeLesson(id: string, remarks = '') {
  return authRequest<ApiLesson>(`/lessons/${id}/complete/`, {
    method: 'POST',
    body: JSON.stringify({ remarks })
  });
}
