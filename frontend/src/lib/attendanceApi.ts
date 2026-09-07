import { API_BASE_URL, getAccessToken, type ApiEnrollment } from './api';
import type { ApiLesson } from './lessonsApi';

export type AttendanceStatus = 'PRESENT' | 'ABSENT' | 'LATE' | 'EXCUSED';
export type RegisterStatus = 'DRAFT' | 'SUBMITTED' | 'LOCKED';

export interface ApiAttendanceRecord {
  id: string;
  student: string;
  student_name: string;
  admission_number: string;
  enrollment: string;
  status: AttendanceStatus;
  remarks: string;
  created_at: string;
  updated_at: string;
}

export interface ApiAttendanceRegister {
  id: string;
  lesson_session: string;
  classroom: string;
  classroom_name: string;
  subject_name: string;
  lesson_date: string;
  status: RegisterStatus;
  submitted_at: string | null;
  locked_at: string | null;
  records: ApiAttendanceRecord[];
  created_at: string;
  updated_at: string;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  if (init.body) headers.set('Content-Type', 'application/json');
  const token = getAccessToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    let message = detail;
    try {
      const parsed = JSON.parse(detail);
      message = Object.entries(parsed).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : String(value)}`).join(' ');
    } catch {}
    throw new Error(message || `Attendance API request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export async function listAttendance(params: { lessonSession?: string; lessonDate?: string } = {}) {
  const query = new URLSearchParams();
  if (params.lessonSession) query.set('lesson_session', params.lessonSession);
  if (params.lessonDate) query.set('lesson_date', params.lessonDate);
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const data = await request<{ results?: ApiAttendanceRegister[] } | ApiAttendanceRegister[]>(`/attendance/${suffix}`);
  return Array.isArray(data) ? data : data.results ?? [];
}

export async function saveAttendance(payload: { lesson_session: string; records: Array<{ enrollment: string; status: AttendanceStatus; remarks?: string }>; submit?: boolean }) {
  return request<ApiAttendanceRegister>('/attendance/bulk/', { method: 'POST', body: JSON.stringify(payload) });
}

export async function lockAttendance(id: string) {
  return request<ApiAttendanceRegister>(`/attendance/${id}/lock/`, { method: 'POST' });
}

export async function listClassEnrollments(classroom: string) {
  const query = new URLSearchParams({ classroom, status: 'ENROLLED' });
  const data = await request<{ results?: ApiEnrollment[] } | ApiEnrollment[]>(`/enrollments/?${query.toString()}`);
  return Array.isArray(data) ? data : data.results ?? [];
}

export type AttendanceLesson = ApiLesson;
