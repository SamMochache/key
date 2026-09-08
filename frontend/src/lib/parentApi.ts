const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');

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
  const token = localStorage.getItem('key_access_token');
  const response = await fetch(`${API_BASE_URL}/parents/me/children/`, {
    headers: { Accept: 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    throw new Error(detail || `Unable to load linked learners (${response.status}).`);
  }

  const data = (await response.json()) as { results?: ParentChild[] };
  return data.results || [];
}

export type { ParentChild };
