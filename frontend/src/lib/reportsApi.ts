import { getAccessToken } from './api';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');

export async function downloadStudentReport(params: {
  student: string;
  academicYear?: string;
  term?: string;
}) {
  const query = new URLSearchParams({ student: params.student });
  if (params.academicYear) query.set('academic_year', params.academicYear);
  if (params.term) query.set('term', params.term);

  const response = await fetch(`${API_BASE_URL}/reports/student/?${query.toString()}`, {
    headers: {
      Accept: 'application/pdf',
      ...(getAccessToken() ? { Authorization: `Bearer ${getAccessToken()}` } : {}),
    },
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    let message = detail || `Unable to generate report (${response.status}).`;
    try {
      const parsed = JSON.parse(detail);
      message = parsed.detail || message;
    } catch {
      // Keep the server response when it is not JSON.
    }
    throw new Error(message);
  }

  const blob = await response.blob();
  const disposition = response.headers.get('Content-Disposition') || '';
  const filenameMatch = disposition.match(/filename="?([^";]+)"?/i);
  const filename = filenameMatch?.[1] || 'student-report.pdf';

  const url = window.URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(url);
}
