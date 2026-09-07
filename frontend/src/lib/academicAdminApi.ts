import { API_BASE_URL, getAccessToken, type ApiAcademicYear, type ApiCambridgeStage, type ApiCurriculum, type ApiMontessoriLevel, type ApiStageSubject, type ApiSubject, type ApiTerm } from './api';

export interface ApiProgramme {
  id: string;
  curriculum: string;
  curriculum_name: string;
  name: string;
  description: string;
  display_order: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  const token = getAccessToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    let message = detail;
    try {
      const parsed = JSON.parse(detail);
      message = Object.entries(parsed).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : String(value)}`).join(' ');
    } catch { /* keep response text */ }
    throw new Error(message || `API request failed (${response.status})`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

async function list<T>(path: string) {
  const data = await request<{ results: T[] } | T[]>(path);
  return Array.isArray(data) ? data : data.results;
}

export const listAcademicYearsAdmin = () => list<ApiAcademicYear>('/academic-years/');
export const listTermsAdmin = (academicYear?: string) => list<ApiTerm>(academicYear ? `/terms/?academic_year=${encodeURIComponent(academicYear)}` : '/terms/');
export const listCurriculaAdmin = () => list<ApiCurriculum>('/curricula/');
export const listProgrammesAdmin = (curriculum?: string) => list<ApiProgramme>(curriculum ? `/programmes/?curriculum=${encodeURIComponent(curriculum)}` : '/programmes/');
export const listSubjectsAdmin = (curriculum?: string) => list<ApiSubject>(curriculum ? `/subjects/?curriculum=${encodeURIComponent(curriculum)}` : '/subjects/');
export const listCambridgeStagesAdmin = (programme?: string) => list<ApiCambridgeStage>(programme ? `/cambridge-stages/?programme=${encodeURIComponent(programme)}` : '/cambridge-stages/');
export const listMontessoriLevelsAdmin = () => list<ApiMontessoriLevel>('/montessori-levels/');
export const listStageSubjectsAdmin = (stage?: string) => list<ApiStageSubject>(stage ? `/stage-subjects/?stage=${encodeURIComponent(stage)}` : '/stage-subjects/');

export const createAcademicYear = (payload: Record<string, unknown>) => request<ApiAcademicYear>('/academic-years/', { method: 'POST', body: JSON.stringify(payload) });
export const updateAcademicYear = (id: string, payload: Record<string, unknown>) => request<ApiAcademicYear>(`/academic-years/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
export const setCurrentAcademicYear = (id: string) => request<ApiAcademicYear>(`/academic-years/${id}/set-current/`, { method: 'POST' });
export const createTerm = (payload: Record<string, unknown>) => request<ApiTerm>('/terms/', { method: 'POST', body: JSON.stringify(payload) });
export const updateTerm = (id: string, payload: Record<string, unknown>) => request<ApiTerm>(`/terms/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
export const setCurrentTerm = (id: string) => request<ApiTerm>(`/terms/${id}/set-current/`, { method: 'POST' });
export const createCurriculum = (payload: Record<string, unknown>) => request<ApiCurriculum>('/curricula/', { method: 'POST', body: JSON.stringify(payload) });
export const updateCurriculum = (id: string, payload: Record<string, unknown>) => request<ApiCurriculum>(`/curricula/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
export const createProgramme = (payload: Record<string, unknown>) => request<ApiProgramme>('/programmes/', { method: 'POST', body: JSON.stringify(payload) });
export const updateProgramme = (id: string, payload: Record<string, unknown>) => request<ApiProgramme>(`/programmes/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
export const createSubject = (payload: Record<string, unknown>) => request<ApiSubject>('/subjects/', { method: 'POST', body: JSON.stringify(payload) });
export const updateSubject = (id: string, payload: Record<string, unknown>) => request<ApiSubject>(`/subjects/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
export const createCambridgeStage = (payload: Record<string, unknown>) => request<ApiCambridgeStage>('/cambridge-stages/', { method: 'POST', body: JSON.stringify(payload) });
export const updateCambridgeStage = (id: string, payload: Record<string, unknown>) => request<ApiCambridgeStage>(`/cambridge-stages/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
export const updateMontessoriLevel = (id: string, payload: Record<string, unknown>) => request<ApiMontessoriLevel>(`/montessori-levels/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
export const createMontessoriLevel = (payload: Record<string, unknown>) => request<ApiMontessoriLevel>('/montessori-levels/', { method: 'POST', body: JSON.stringify(payload) });
export const createStageSubject = (payload: Record<string, unknown>) => request<ApiStageSubject>('/stage-subjects/', { method: 'POST', body: JSON.stringify(payload) });
export const updateStageSubject = (id: string, payload: Record<string, unknown>) => request<ApiStageSubject>(`/stage-subjects/${id}/`, { method: 'PATCH', body: JSON.stringify(payload) });
