import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { listAssistants, createAssistant, createConversation, listConversations } from '../services/api';

type Conversation = {
  id: string;
  title?: string | null;
  created_at?: string;
};

const apiBase = (import.meta as any).env?.VITE_API_URL || '';

export default function ConversationsPage() {
  const [items, setItems] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [preparedConvId, setPreparedConvId] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${apiBase}/api/v1/conversations/`);
        if (!res.ok) throw new Error(String(res.status));
        const data = await res.json();
        setItems(data || []);
        // Pre-create a conversation to make the CTA immediate when list is empty
        if ((!data || data.length === 0)) {
          try {
            let assistants = [] as any[];
            try { assistants = await listAssistants(1, 0); } catch {}
            let assistantId: string | null = assistants?.[0]?.id || null;
            if (!assistantId) {
              const asst = await createAssistant('AutoBot');
              assistantId = asst?.id ?? null;
            }
            if (assistantId) {
              const conv = await createConversation(assistantId, 'New Conversation');
              if (conv?.id) setPreparedConvId(conv.id as string);
            }
          } catch {}
        }
      } catch (e: any) {
        setError(e?.message || 'failed');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="p-4">Loading...</div>;

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-xl font-semibold">Conversations</h2>
      <div>
        <button
          onClick={async () => {
            try {
              setCreating(true);
              // If prepared conversation exists, navigate immediately
              if (preparedConvId) {
                window.location.assign(`/chat/${preparedConvId}`);
                return;
              }
              // ensure we have at least one assistant
              let assistants = [] as any[];
              try { assistants = await listAssistants(1, 0); } catch {}
              let assistantId: string | null = assistants?.[0]?.id || null;
              if (!assistantId) {
                try {
                  const asst = await createAssistant('AutoBot');
                  assistantId = asst?.id ?? null;
                } catch {}
              }
              if (!assistantId) throw new Error('No assistant available');
              // create conversation then navigate
              const conv = await createConversation(assistantId, 'New Conversation');
              if (conv?.id) {
                window.location.assign(`/chat/${conv.id}`);
                return;
              }
              // fallback: navigate to the most recent conversation if exists
              const convs = await listConversations(1, 0);
              if (convs?.[0]?.id) {
                window.location.assign(`/chat/${convs[0].id}`);
                return;
              }
              throw new Error('Failed to create conversation');
            } catch (e: any) {
              setError(e?.message || 'failed to create');
            } finally {
              setCreating(false);
            }
          }}
          className="px-3 py-1 rounded bg-black text-white"
          disabled={creating}
        >
          {creating ? 'Creating...' : 'New Conversation'}
        </button>
      </div>
      {error && <div className="text-red-600">Error: {error}</div>}
      {items.length === 0 && !error && <div className="text-gray-500">No conversations yet.</div>}
      <ul className="space-y-2">
        {items.map((c) => (
          <li key={c.id} className="border rounded p-2 flex justify-between items-center">
            <div>
              <div className="font-medium">{c.title || '(untitled)'}</div>
              <div className="text-xs text-gray-500">{c.created_at || ''}</div>
            </div>
            <Link className="px-3 py-1 rounded bg-black text-white" to={`/chat/${c.id}`}>
              Open
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
