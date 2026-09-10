import { authRequest } from './authRequest';
import type { ApiEnrollment } from './api';
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

export async function listAttendance(params: { lessonSession?: string; lessonDate?: string; classroom?: string; student?: string } = {}) {
  const query = new URLSearchParams();
  if (params.lessonSession) query.set('lesson_session', params.lessonSession);
  if (params.lessonDate) query.set('lesson_date', params.lessonDate);
  if (params.classroom) query.set('classroom', params.classroom);
  if (params.student) query.set('student', params.student);
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const data = await authRequest<{ results?: ApiAttendanceRegister[] } | ApiAttendanceRegister[]>(`/attendance/${suffix}`);
  return Array.isArray(data) ? data : data.results ?? [];
}

export async function saveAttendance(payload: { lesson_session: string; records: Array<{ enrollment: string; status: AttendanceStatus; remarks?: string }>; submit?: boolean }) {
  return authRequest<ApiAttendanceRegister>('/attendance/bulk/', { method: 'POST', body: JSON.stringify(payload) });
}

export async function lockAttendance(id: string) {
  return authRequest<ApiAttendanceRegister>(`/attendance/${id}/lock/`, { method: 'POST' });
}

export async function listClassEnrollments(classroom: string) {
  const query = new URLSearchParams({ classroom, status: 'ENROLLED' });
  const data = await authRequest<{ results?: ApiEnrollment[] } | ApiEnrollment[]>(`/enrollments/?${query.toString()}`);
  return Array.isArray(data) ? data : data.results ?? [];
}

export type AttendanceLesson = ApiLesson;
