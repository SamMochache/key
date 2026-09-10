import { authRequest } from './authRequest';

interface ParentChild {
  id: string;
  full_name: string;
  first_name: string;
  initials: string;
  profile_photo: string | null;
  admission_number: string;
  date_of_birth: string;
  age: number | null;
  school: string;
  school_name: string;
  relationship: string;
  can_view_reports: boolean;
  is_primary_contact: boolean;
  classroom: {
    id: string;
    name: string;
    academic_year: string;
    term: number;
    status: string;
  } | null;
  attendance_rate: number | null;
  growth_index: number | null;
  latest_portfolio: {
    id: string;
    title: string;
    description: string;
    event_date: string | null;
    item_type: string;
  } | null;
}

export async function listMyChildren(): Promise<ParentChild[]> {
  const data = await authRequest<{ results?: ParentChild[] }>('/parents/me/children/');
  return data.results || [];
}

export type { ParentChild };
