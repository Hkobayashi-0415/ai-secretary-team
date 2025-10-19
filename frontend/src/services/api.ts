export type Message = {
  id: string;
  role: 'user' | 'assistant' | 'system' | string;
  content: string;
};

export type MessagePage = {
  messages: Message[];
  has_more: boolean;
};

const baseUrl = (import.meta as any).env?.VITE_API_URL || '';
const apiBase = `${baseUrl}/api/v1`;

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

