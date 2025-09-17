import { useEffect, useRef, useState } from 'react';
import { useChatStore } from '../store/chat';

const API_BASE = import.meta.env.VITE_API_URL?.replace(/\/$/, '') || '';

export default function ChatPage({ conversationId }: { conversationId: string }) {
  const { messages, push } = useChatStore();
  const [input, setInput] = useState('');
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const wsUrl = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host.replace(/:3000$/, ':8000');
    const ws = new WebSocket(`${wsUrl}/ws/chat?conversation_id=${conversationId}`);
    ws.onmessage = (ev) => {
      const data = JSON.parse(ev.data);
      if (data.type === 'assistant_start') {
        push({ id: crypto.randomUUID(), role: 'assistant', content: '' });
      } else if (data.type === 'token') {
        // 直近assistantに追記（簡易実装）
        messages[messages.length - 1].content += data.text;
      } else if (data.type === 'assistant_end') {
        // noop
      }
    };
    wsRef.current = ws;
    return () => ws.close();
  }, [conversationId]);

  const send = () => {
    if (!input) return;
    push({ id: crypto.randomUUID(), role: 'user', content: input });
    wsRef.current?.send(JSON.stringify({ type: 'user_message', text: input }));
    setInput('');
  };

  return (
    <div className="p-4 max-w-2xl mx-auto">
      <div className="space-y-3 mb-4">
        {messages.map((m) => (
          <div key={m.id} className={m.role === 'user' ? 'text-right' : 'text-left'}>
            <div className="inline-block rounded-2xl px-4 py-2 shadow">{m.content}</div>
          </div>
        ))}
      </div>
      <div className="flex gap-2">
        <input className="border rounded px-3 py-2 flex-1" value={input} onChange={(e)=>setInput(e.target.value)} placeholder="Type message..." />
        <button className="px-4 py-2 rounded bg-black text-white" onClick={send}>Send</button>
      </div>
    </div>
  );
}
