import { getAccessToken } from './api';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export interface NotificationItem {
  id: string;
  title: string;
  body: string;
  type: string;
  link: string;
  is_read: boolean;
  created_at: string;
  read_at: string | null;
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getAccessToken();
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(options.headers || {}) },
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || 'Unable to load notifications.');
  }
  return response.json();
}

export function listNotifications(unreadOnly = false) {
  return request<{ results: NotificationItem[]; unread_count: number }>(`/notifications/${unreadOnly ? '?unread=true' : ''}`);
}

export function markNotificationRead(id: string) {
  return request<{ id: string; is_read: boolean }>(`/notifications/${id}/read/`, { method: 'POST' });
}

export function markAllNotificationsRead() {
  return request<{ marked_read: number }>('/notifications/mark-all-read/', { method: 'POST' });
}
