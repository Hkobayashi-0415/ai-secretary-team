import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

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

  useEffect(() => {
    (async () => {
      try {
        const res = await fetch(`${apiBase}/api/v1/conversations/`);
        if (!res.ok) throw new Error(String(res.status));
        const data = await res.json();
        setItems(data || []);
      } catch (e: any) {
        setError(e?.message || 'failed');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  if (loading) return <div className="p-4">Loading...</div>;
  if (error) return <div className="p-4 text-red-600">Error: {error}</div>;

  return (
    <div className="p-4 space-y-3">
      <h2 className="text-xl font-semibold">Conversations</h2>
      {items.length === 0 && <div className="text-gray-500">No conversations yet.</div>}
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

