import { API_BASE_URL, getAccessToken } from './api';

export type AssessmentStatus = 'DRAFT' | 'PUBLISHED' | 'CLOSED';
export type SubmissionStatus = 'DRAFT' | 'SUBMITTED' | 'RETURNED' | 'GRADED';
export interface ApiAssessment { id:string; lesson_session:string; lesson_session_title:string; teacher:string; teacher_name:string; title:string; description:string; assessment_type:string; status:AssessmentStatus; due_date:string|null; maximum_score:string|null; allow_resubmission:boolean; rubric?:ApiRubric|null; created_at:string; updated_at:string; }
export interface ApiRubricCriterion { id:string; title:string; description:string; maximum_score:string; sequence:number; }
export interface ApiRubric { id:string; title:string; description:string; criteria:ApiRubricCriterion[]; }
export interface ApiSubmission { id:string; assessment:string; enrollment:string; student_name:string; admission_number:string; submitted_at:string|null; submission_text:string; submission_url:string; status:SubmissionStatus; is_late:boolean; teacher_notes:string; submitted_by:string; created_at:string; updated_at:string; }
export interface ApiEvaluation { id:string; submission:string; student_name:string; total_score:string|null; percentage:string|null; narrative_feedback:string; published:boolean; published_at:string|null; criterion_scores:ApiCriterionScore[]; competency_evaluations:unknown[]; }
export interface ApiCriterionScore { id:string; evaluation:string; criterion:string; score:string|null; feedback:string; }
interface Paginated<T>{results:T[];count:number;next:string|null;previous:string|null;}
async function request<T>(path:string,init:RequestInit={}):Promise<T>{const headers=new Headers(init.headers);headers.set('Accept','application/json');if(init.body&&!headers.has('Content-Type'))headers.set('Content-Type','application/json');const token=getAccessToken();if(token)headers.set('Authorization',`Bearer ${token}`);const response=await fetch(`${API_BASE_URL}${path}`,{...init,headers});if(!response.ok){const detail=await response.text().catch(()=> '');let message=detail;try{const parsed=JSON.parse(detail);message=Object.entries(parsed).map(([k,v])=>`${k}: ${Array.isArray(v)?v.join(', '):String(v)}`).join(' ');}catch{}throw new Error(message||`Assessment API request failed (${response.status})`);}if(response.status===204)return undefined as T;return response.json() as Promise<T>}
function list<T>(path:string){return request<Paginated<T>|T[]>(path).then(d=>Array.isArray(d)?d:d.results)}
export const listAssessments=(p:{status?:string;lessonSession?:string}={})=>{const q=new URLSearchParams();if(p.status)q.set('status',p.status);if(p.lessonSession)q.set('lesson_session',p.lessonSession);return list<ApiAssessment>(`/assessments/${q.toString()?`?${q}`:''}`)};
export const createAssessment=(p:Record<string,unknown>)=>request<ApiAssessment>('/assessments/',{method:'POST',body:JSON.stringify(p)});
export const updateAssessment=(id:string,p:Record<string,unknown>)=>request<ApiAssessment>(`/assessments/${id}/`,{method:'PATCH',body:JSON.stringify(p)});
export const listSubmissions=(assessment?:string)=>list<ApiSubmission>(`/submissions/${assessment?`?assessment=${encodeURIComponent(assessment)}`:''}`);
export const requestSubmission=(p:Record<string,unknown>)=>request<ApiSubmission>('/submissions/',{method:'POST',body:JSON.stringify(p)});
export const createEvaluation=(p:Record<string,unknown>)=>request<ApiEvaluation>('/evaluations/',{method:'POST',body:JSON.stringify(p)});
export const updateEvaluation=(id:string,p:Record<string,unknown>)=>request<ApiEvaluation>(`/evaluations/${id}/`,{method:'PATCH',body:JSON.stringify(p)});
export const listEvaluations=(submission?:string)=>list<ApiEvaluation>(`/evaluations/${submission?`?submission=${encodeURIComponent(submission)}`:''}`);
export const createCriterionScore=(p:Record<string,unknown>)=>request<ApiCriterionScore>('/criterion-scores/',{method:'POST',body:JSON.stringify(p)});
export const updateCriterionScore=(id:string,p:Record<string,unknown>)=>request<ApiCriterionScore>(`/criterion-scores/${id}/`,{method:'PATCH',body:JSON.stringify(p)});
export const publishEvaluation=(id:string)=>request<ApiEvaluation>(`/evaluations/${id}/publish/`,{method:'POST'});
export const createRubric=(p:Record<string,unknown>)=>request<ApiRubric>('/rubrics/',{method:'POST',body:JSON.stringify(p)});
export const createRubricCriterion=(p:Record<string,unknown>)=>request<ApiRubricCriterion>('/rubric-criteria/',{method:'POST',body:JSON.stringify(p)});
