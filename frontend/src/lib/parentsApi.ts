import { authRequest } from './authRequest';

export interface ParentStudentLink {
  id: string;
  name: string;
  admission_number: string;
  relationship: string;
  can_view_reports: boolean;
  is_primary_contact: boolean;
}

export interface ApiParent {
  id: string;
  user: string;
  full_name: string;
  email: string;
  phone_number: string;
  school: string;
  school_name: string;
  is_active: boolean;
  students: ParentStudentLink[];
}

export interface ParentDashboardChild {
  id: string;
  full_name: string;
  first_name: string;
  initials: string;
  profile_photo: string | null;
  admission_number: string;
  date_of_birth: string;
  age: number;
  school: string;
  school_name: string;
  relationship: string;
  can_view_reports: boolean;
  is_primary_contact: boolean;
  classroom: null | {
    id: string;
    name: string;
    academic_year: string;
    term: number;
    status: string;
  };
  attendance_rate: number | null;
  growth_index: number | null;
  latest_portfolio: null | {
    id: string;
    title: string;
    description: string;
    event_date: string;
    item_type: string;
  };
}

export async function listParents(search?: string) {
  const suffix = search?.trim() ? `?search=${encodeURIComponent(search.trim())}` : '';
  return authRequest<{ results: ApiParent[] }>(`/parents/${suffix}`);
}

export async function listMyChildren() {
  return authRequest<{ results: ParentDashboardChild[] }>('/parents/me/children/');
}

export async function createParent(payload: {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  phone_number?: string;
  school: string;
  student: string;
  relationship?: string;
  can_view_reports?: boolean;
  is_primary_contact?: boolean;
}) {
  return authRequest<ApiParent & { student: ParentStudentLink }>('/parents/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateParent(id: string, payload: Record<string, unknown>) {
  return authRequest<{ id: string; full_name: string; is_active: boolean }>('/parents/', {
    method: 'PATCH',
    body: JSON.stringify({ id, ...payload }),
  });
}
