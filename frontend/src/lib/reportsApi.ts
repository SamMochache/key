import { getAccessToken } from './api';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');
const REFRESH_TOKEN_KEY = 'key_refresh_token';
const ACCESS_TOKEN_KEY = 'key_access_token';

async function refreshReportAccessToken() {
  const refresh = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!refresh) return null;
  const response = await fetch(`${API_BASE_URL}/auth/token/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify({ refresh }),
  });
  if (!response.ok) return null;
  const data = await response.json().catch(() => ({} as { access?: string; refresh?: string }));
  if (!data.access) return null;
  localStorage.setItem(ACCESS_TOKEN_KEY, data.access);
  if (data.refresh) localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh);
  return data.access;
}

async function downloadPdf(path: string, params: Record<string, string>, retry = true) {
  const query = new URLSearchParams(params);
  const token = getAccessToken();
  const response = await fetch(`${API_BASE_URL}${path}?${query.toString()}`, {
    headers: {
      Accept: '*/*',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  if (response.status === 401 && retry) {
    const refreshed = await refreshReportAccessToken();
    if (refreshed) return downloadPdf(path, params, false);
  }

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

export interface PublishedAINarrativeResponse {
  id: string;
  student: string;
  student_name: string;
  academic_year: string;
  academic_year_name: string;
  term: string;
  term_number: number;
  narrative: AINarrativeResponse['narrative'];
  facts: AINarrativeResponse['facts'];
  published_at: string | null;
}

function normalizePublishedAIReport(report: any): PublishedAINarrativeResponse {
  const rawFacts = report?.facts && typeof report.facts === 'object' ? report.facts : {};
  const rawNarrative = report?.narrative && typeof report.narrative === 'object' ? report.narrative : {};

  const learner = rawFacts.learner && typeof rawFacts.learner === 'object' ? rawFacts.learner : {};
  const period = rawFacts.period && typeof rawFacts.period === 'object' ? rawFacts.period : {};
  const assessment = rawFacts.assessment && typeof rawFacts.assessment === 'object' ? rawFacts.assessment : {};
  const attendance = rawFacts.attendance && typeof rawFacts.attendance === 'object' ? rawFacts.attendance : {};
  const portfolio = rawFacts.portfolio && typeof rawFacts.portfolio === 'object' ? rawFacts.portfolio : {};

  const narrative = {
    summary: String(rawNarrative.summary ?? rawNarrative.overall_progress ?? ''),
    strengths: String(rawNarrative.strengths ?? ''),
    development_areas: String(rawNarrative.development_areas ?? ''),
    next_steps: String(rawNarrative.next_steps ?? rawNarrative.suggested_next_steps ?? ''),
    teacher_note: String(rawNarrative.teacher_note ?? rawNarrative.teacher_review_note ?? ''),
  };

  return {
    id: String(report?.id ?? ''),
    student: String(report?.student ?? rawFacts.student_id ?? ''),
    student_name: String(report?.student_name ?? rawFacts.student_name ?? learner.first_name ?? 'Learner'),
    academic_year: String(report?.academic_year ?? ''),
    academic_year_name: String(report?.academic_year_name ?? period.academic_year ?? rawFacts.academic_year ?? ''),
    term: String(report?.term ?? ''),
    term_number: Number(report?.term_number ?? period.term ?? rawFacts.term_number ?? 0),
    narrative,
    facts: {
      learner: {
        first_name: String(learner.first_name ?? rawFacts.student_name?.split?.(' ')?.[0] ?? 'Learner'),
        admission_number: String(learner.admission_number ?? rawFacts.admission_number ?? ''),
        class: String(learner.class ?? 'Not recorded'),
        stage: learner.stage == null ? null : String(learner.stage),
      },
      period: {
        academic_year: String(period.academic_year ?? rawFacts.academic_year ?? report?.academic_year_name ?? ''),
        term: Number(period.term ?? rawFacts.term_number ?? report?.term_number ?? 0),
      },
      assessment: {
        published_results: Number(assessment.published_results ?? 0),
        average_percentage: assessment.average_percentage == null ? null : Number(assessment.average_percentage),
      },
      attendance: {
        recorded_sessions: Number(attendance.recorded_sessions ?? 0),
        attendance_percentage: attendance.attendance_percentage == null ? null : Number(attendance.attendance_percentage),
      },
      competencies: Array.isArray(rawFacts.competencies) ? rawFacts.competencies : [],
      portfolio: {
        items: Number(portfolio.items ?? 0),
        artifacts: Number(portfolio.artifacts ?? 0),
      },
    },
    published_at: report?.published_at ?? null,
  };
}

async function jsonRequest(path: string, options: RequestInit = {}, retry = true) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
      ...(options.headers || {}),
    },
  });

  if (response.status === 401 && retry) {
    const refreshed = await refreshReportAccessToken();
    if (refreshed) return jsonRequest(path, options, false);
  }

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

export async function listPublishedAINarrativeReports(params: { student?: string; academicYear?: string; term?: string } = {}) {
  const query = new URLSearchParams();
  if (params.student) query.set('student', params.student);
  if (params.academicYear) query.set('academic_year', params.academicYear);
  if (params.term) query.set('term', params.term);
  const suffix = query.toString() ? `?${query.toString()}` : '';
  const payload = await jsonRequest(`/reports/ai-narrative/published/${suffix}`) as { results?: unknown[] };
  return {
    results: Array.isArray(payload.results) ? payload.results.map(normalizePublishedAIReport) : [],
  };
}

export async function downloadPublishedAINarrativePdf(id: string) {
  return downloadPdf(`/reports/ai-narrative/${id}/pdf/`, {});
}
