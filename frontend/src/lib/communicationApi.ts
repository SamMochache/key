import { getAccessToken } from './api';

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api').replace(/\/$/, '');

export interface CommunicationMessage { id: string; school: string; sender: string; sender_name: string; sender_email: string; recipient: string; recipient_name: string; recipient_email: string; subject: string; body: string; sent_at: string; read_at: string | null; is_read: boolean; }
export interface CommunicationContact { id: string; name: string; email: string; }
interface Paginated<T> { results: T[]; count: number; }

async function request<T>(path: string, init: RequestInit = {}) {
  const token = getAccessToken();
  const headers = new Headers(init.headers);
  headers.set('Accept', 'application/json');
  if (init.body && !headers.has('Content-Type')) headers.set('Content-Type', 'application/json');
  if (token) headers.set('Authorization', `Bearer ${token}`);
  const response = await fetch(`${API_BASE_URL}${path}`, { ...init, headers });
  const text = await response.text();
  let data: any = {};
  try { data = text ? JSON.parse(text) : {}; } catch { /* handled below */ }
  if (!response.ok) {
    const message = data?.detail || Object.entries(data).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(', ') : String(value)}`).join(' ') || `Request failed (${response.status})`;
    throw new Error(message);
  }
  return data as T;
}

export async function listMessages(folder: 'inbox' | 'sent' = 'inbox') {
  const data = await request<Paginated<CommunicationMessage> | CommunicationMessage[]>(`/messages/?folder=${folder}`);
  return Array.isArray(data) ? data : data.results;
}

export async function listContacts(search = '') {
  const query = search ? `?search=${encodeURIComponent(search)}` : '';
  return request<CommunicationContact[]>(`/communication/contacts/${query}`);
}

export function sendMessage(payload: { recipient: string; subject: string; body: string; school?: string }) {
  return request<CommunicationMessage>('/messages/', { method: 'POST', body: JSON.stringify(payload) });
}

export function markMessageRead(id: string) {
  return request<CommunicationMessage>(`/messages/${id}/read/`, { method: 'POST' });
}
