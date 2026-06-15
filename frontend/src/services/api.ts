const API_BASE = '/api';

function getToken(): string | null {
  return localStorage.getItem('token');
}

export function setToken(token: string) {
  localStorage.setItem('token', token);
}

export function clearToken() {
  localStorage.removeItem('token');
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };
  if (token) headers.Authorization = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || 'Request failed');
  }
  return res.json();
}

export interface User {
  id: number;
  email: string;
  name: string;
  avatar: string | null;
  onboarding_complete: boolean;
}

export interface PatientProfile {
  full_name: string;
  age: number;
  gender: string;
  address: string;
  phone: string;
  medical_history: string | null;
  language: string;
  onboarding_complete: boolean;
}

export interface ChatMessage {
  id: number;
  role: string;
  content: string;
  created_at: string;
  triage_department?: string | null;
  triage_confidence?: number | null;
}

export interface ChatSession {
  id: number;
  language: string;
  started_at: string;
  is_active: boolean;
  message_count: number;
}

export const api = {
  register: (email: string, password: string, name: string) =>
    request<{ access_token: string; user: User }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, name }),
    }),

  login: (email: string, password: string) =>
    request<{ access_token: string; user: User }>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<User>('/auth/me'),

  googleAuthUrl: () => request<{ url: string }>('/auth/google'),

  getProfile: () => request<PatientProfile | null>('/user/profile'),

  saveProfile: (profile: Omit<PatientProfile, 'onboarding_complete'>) =>
    request<PatientProfile>('/user/profile', {
      method: 'PUT',
      body: JSON.stringify(profile),
    }),

  createSession: () => request<ChatSession>('/chat/session', { method: 'POST' }),

  listSessions: () => request<ChatSession[]>('/chat/sessions'),

  getMessages: (sessionId: number) =>
    request<ChatMessage[]>(`/chat/session/${sessionId}/messages`),

  sendMessage: (content: string, sessionId: number) =>
    request<ChatMessage>('/chat/message', {
      method: 'POST',
      body: JSON.stringify({ content, session_id: sessionId }),
    }),

  endSession: (sessionId: number) =>
    request<{ message: string }>(`/chat/session/${sessionId}/end`, { method: 'POST' }),

  tts: async (text: string, language: string): Promise<Blob> => {
    const token = getToken();
    const res = await fetch(`${API_BASE}/voice/tts`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ text, language }),
    });
    if (!res.ok) throw new Error('TTS failed');
    return res.blob();
  },
};
