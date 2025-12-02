export type Message = {
  id: string;
  role: 'user' | 'assistant' | 'system' | string;
  content: string;
};

export type MessagePage = {
  messages: Message[];
  has_more: boolean;
};

// Normalize API base to avoid "/api/api/..." duplication.
const rawBase = (import.meta as any).env?.VITE_API_URL || '';
let trimmed = String(rawBase).replace(/\/$/, '');
// Normalize common inputs:
// - "/api/v1" -> "/api"
// - "/api/v1/" -> "/api"
trimmed = trimmed.replace(/\/api\/v1$/i, '/api');

// If the env already includes /api, don't append another /api.
const apiPrefix = trimmed
  ? (trimmed.endsWith('/api') ? trimmed : `${trimmed}/api`)
  : '/api';
const apiBase = `${apiPrefix}/v1`;

async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${apiBase}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`${res.status}`);
  }
  return res.json() as Promise<T>;
}

export async function listMessagesPaged(
  conversationId: string,
  beforeId?: string,
  limit: number = 20,
): Promise<MessagePage> {
  const params = new URLSearchParams();
  if (beforeId) params.set('before_id', beforeId);
  if (limit) params.set('limit', String(limit));
  return http<MessagePage>(`/conversations/${conversationId}/messages/page?${params.toString()}`);
}

export async function getConversation(conversationId: string): Promise<any> {
  return http<any>(`/conversations/${conversationId}`);
}

export async function getAssistant(assistantId: string): Promise<any> {
  return http<any>(`/assistants/${assistantId}`);
}

export async function listAssistants(limit: number = 50, skip: number = 0): Promise<any[]> {
  const params = new URLSearchParams();
  params.set('limit', String(limit));
  params.set('skip', String(skip));
  return http<any[]>(`/assistants/?${params.toString()}`);
}

export async function createAssistant(name: string): Promise<any> {
  return http<any>(`/assistants/`, {
    method: 'POST',
    body: JSON.stringify({ name }),
  });
}

export async function createConversation(assistantId: string, title?: string): Promise<any> {
  return http<any>(`/conversations/`, {
    method: 'POST',
    body: JSON.stringify({ assistant_id: assistantId, title: title || 'New Conversation' }),
  });
}

export async function listConversations(limit: number = 20, offset: number = 0): Promise<any[]> {
  const params = new URLSearchParams();
  params.set('limit', String(limit));
  params.set('offset', String(offset));
  return http<any[]>(`/conversations/?${params.toString()}`);
}
