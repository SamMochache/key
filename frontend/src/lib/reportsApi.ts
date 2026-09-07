import { getAccessToken } from './api';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');

async function downloadPdf(path: string, params: Record<string, string>) {
  const query = new URLSearchParams(params);
  const response = await fetch(`${API_BASE_URL}${path}?${query.toString()}`, {
    headers: {
      Accept: 'application/pdf',
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
    },
  });
  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    let message = detail || `Unable to generate report (${response.status}).`;
    try { const parsed = JSON.parse(detail); message = parsed.detail || message; } catch { /* Keep non-JSON response. */ }
    throw new Error(message);
  }
  const blob = await response.blob();
  const disposition = response.headers.get('Content-Disposition') || '';
  const filenameMatch = disposition.match(/filename="?([^";]+)"?/i);
  const filename = filenameMatch?.[1] || 'report.pdf';
  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(url);
}

function reportQuery(params: { classroom?: string; student?: string; academicYear?: string; term?: string }) {
  const query: Record<string, string> = {};
  if (params.classroom) query.classroom = params.classroom;
  if (params.student) query.student = params.student;
  if (params.academicYear) query.academic_year = params.academicYear;
  if (params.term) query.term = params.term;
  return query;
}

export async function downloadStudentReport(params: { student: string; academicYear?: string; term?: string }) {
  const query: Record<string, string> = { student: params.student };
  if (params.academicYear) query.academic_year = params.academicYear;
  if (params.term) query.term = params.term;
  return downloadPdf('/reports/student/', query);
}
export async function downloadClassReport(params: { classroom: string; academicYear?: string; term?: string }) {
  const query: Record<string, string> = { classroom: params.classroom };
  if (params.academicYear) query.academic_year = params.academicYear;
  if (params.term) query.term = params.term;
  return downloadPdf('/reports/class/', query);
}
export async function downloadAttendanceReport(params: { classroom?: string; student?: string; academicYear?: string; term?: string }) { return downloadPdf('/reports/attendance/', reportQuery(params)); }
export async function downloadAssessmentResultsReport(params: { classroom?: string; student?: string; academicYear?: string; term?: string }) { return downloadPdf('/reports/assessments/', reportQuery(params)); }
export async function downloadCompetencyOutcomesReport(params: { classroom?: string; student?: string; academicYear?: string; term?: string }) { return downloadPdf('/reports/competencies/', reportQuery(params)); }
export async function downloadPortfolioEvidenceReport(params: { classroom?: string; student?: string; academicYear?: string; term?: string }) { return downloadPdf('/reports/portfolio/', reportQuery(params)); }
export async function downloadConsolidatedReport(params: { classroom?: string; student?: string; academicYear: string; term: string }) { return downloadPdf('/reports/consolidated/', reportQuery(params)); }

export interface AINarrativeResponse {
  id: string;
  status: 'DRAFT' | 'REVIEWED' | 'PUBLISHED';
  student: string;
  academic_year: string;
  term: string;
  facts: {
    learner: { first_name: string; admission_number: string; class: string; stage: string | null };
    period: { academic_year: string; term: number };
    assessment: { published_results: number; average_percentage: number | null };
    attendance: { recorded_sessions: number; attendance_percentage: number | null };
    competencies: Array<{ name: string; observations: number; highest_level: string; average_level: number | null }>;
    portfolio: { items: number; artifacts: number };
  };
  narrative: {
    summary: string;
    strengths: string;
    development_areas: string;
    next_steps: string;
    teacher_note: string;
  };
  generated_content: AINarrativeResponse['narrative'];
  edited_content: Partial<AINarrativeResponse['narrative']>;
  review_required: boolean;
  model: string;
  generated_at: string;
  reviewed_at: string | null;
  published_at: string | null;
}

async function jsonRequest(path: string, options: RequestInit = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
      ...(options.headers || {}),
    },
  });
  const detail = await response.text().catch(() => '');
  let payload: any = {};
  try { payload = detail ? JSON.parse(detail) : {}; } catch { /* handled below */ }
  if (!response.ok) throw new Error(payload.detail || `Request failed (${response.status}).`);
  return payload;
}

export async function generateAINarrativeReport(params: { student: string; academicYear: string; term: string }) {
  return jsonRequest('/reports/ai-narrative/', {
    method: 'POST',
    body: JSON.stringify({ student: params.student, academic_year: params.academicYear, term: params.term }),
  }) as Promise<AINarrativeResponse>;
}

export async function listAINarrativeReports(params: { student?: string; academicYear?: string; term?: string } = {}) {
  const query = new URLSearchParams();
  if (params.student) query.set('student', params.student);
  if (params.academicYear) query.set('academic_year', params.academicYear);
  if (params.term) query.set('term', params.term);
  const suffix = query.toString() ? `?${query.toString()}` : '';
  return jsonRequest(`/reports/ai-narrative/${suffix}`) as Promise<{ results: AINarrativeResponse[] }>;
}

export async function saveAINarrativeReport(id: string, narrative: AINarrativeResponse['narrative']) {
  return jsonRequest('/reports/ai-narrative/', {
    method: 'PATCH',
    body: JSON.stringify({ id, narrative }),
  }) as Promise<AINarrativeResponse>;
}

export async function publishAINarrativeReport(id: string) {
  return jsonRequest(`/reports/ai-narrative/${id}/publish/`, { method: 'POST' }) as Promise<AINarrativeResponse>;
}
