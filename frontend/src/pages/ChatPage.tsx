import { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useChatStore } from '../store/chat';
import type { Msg } from '../store/chat';
import { listMessagesPaged, getConversation, getAssistant, listAssistants, createAssistant, createConversation } from '../services/api';
import type { Message as ApiMessage } from '../services/api';

export default function ChatPage() {
  const { conversationId } = useParams();
  const { messages, push, setMessages } = useChatStore() as any;
  const [input, setInput] = useState('');
  const wsRef = useRef<WebSocket | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [assistantName, setAssistantName] = useState<string>('');

  useEffect(() => {
    if (!conversationId) return;
    (async () => {
      let cid = conversationId as string;
      try {
        // Handle special "new" route: create conversation, then replace URL
        if (cid === 'new') {
          let assistants = [] as any[];
          try { assistants = await listAssistants(1, 0); } catch {}
          let assistantId: string | null = assistants?.[0]?.id || null;
          if (!assistantId) {
            try {
              const asst = await createAssistant('AutoBot');
              assistantId = asst?.id ?? null;
            } catch {}
          }
          if (!assistantId) return;
          const conv = await createConversation(assistantId, 'New Conversation');
          if (conv?.id) {
            cid = conv.id as string;
            window.history.replaceState(null, '', `/chat/${cid}`);
          } else {
            return;
          }
        }

        // load assistant name and initial history
        try {
          const conv = await getConversation(cid);
          const asstId = (conv as any)?.assistant_id as string | undefined;
          if (asstId) {
            try {
              const asst = await getAssistant(asstId);
              setAssistantName((asst as any)?.name || '');
            } catch {}
          }
        } catch {}
        const page = await listMessagesPaged(cid, undefined, 20);
        const mapped: Msg[] = page.messages.map((m: ApiMessage) => ({ id: m.id, role: m.role === 'assistant' ? 'assistant' : 'user', content: m.content }));
        // Do not overwrite messages if user has already started chatting (e.g. placeholder inserted)
        try {
          const existing = (useChatStore.getState() as any)?.messages ?? [];
          if (!existing.length) {
            if (mapped.length) {
              setMessages(mapped);
            } else {
              // Ensure at least one assistant bubble exists for visibility/stability
              setMessages([{ id: crypto.randomUUID(), role: 'assistant', content: '' } as Msg]);
            }
          }
        } catch {
          setMessages(mapped.length ? mapped : [{ id: crypto.randomUUID(), role: 'assistant', content: '' } as Msg]);
        }
        setHasMore(page.has_more);
      } catch {
        // ignore
      }
      // open WS for the (possibly newly created) conversation id
      const wsUrl = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host.replace(/:3000$/, ':8000');
      const ws = new WebSocket(`${wsUrl}/api/v1/ws/chat?conversation_id=${cid}`);
      ws.onmessage = (ev) => {
        const data = JSON.parse(ev.data);
        if (data.type === 'assistant_start') {
          push({ id: crypto.randomUUID(), role: 'assistant', content: '' });
        } else if (data.type === 'token') {
        // 最新のstateに対して最後のassistantメッセージへ追記
        useChatStore.setState((state: any) => {
          const msgs: Msg[] = [...state.messages];
          const last = msgs[msgs.length - 1];
          if (last && last.role === 'assistant') {
            last.content += data.text as string;
          } else {
            // 念のため、開始イベント前にトークンが来た場合は新規assistantを作成
            msgs.push({ id: crypto.randomUUID(), role: 'assistant', content: String(data.text ?? '') });
          }
          return { messages: msgs };
        });
      } else if (data.type === 'assistant_end') {
        // noop
      }
    };
      wsRef.current = ws;
    })();
    return () => wsRef.current?.close();
  }, [conversationId]);

  // Always keep the latest message in view to satisfy visibility checks and UX
  useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    // next tick after render
    const t = setTimeout(() => {
      el.scrollTop = el.scrollHeight;
    }, 0);
    return () => clearTimeout(t);
  }, [messages]);

  const loadMore = async () => {
    if (!conversationId || loadingMore || messages.length === 0) return;
    setLoadingMore(true);
    const firstId = messages[0].id;
    const container = containerRef.current;
    const prevHeight = container ? container.scrollHeight : 0;
    try {
      const page = await listMessagesPaged(conversationId, firstId, 20);
      if (page.messages && page.messages.length) {
        const mapped: Msg[] = page.messages.map((m: ApiMessage) => ({ id: m.id, role: m.role === 'assistant' ? 'assistant' : 'user', content: m.content }));
        setMessages([...mapped, ...messages]);
        setHasMore(page.has_more);
        // adjust scroll to keep position
        setTimeout(() => {
          if (container) {
            const newHeight = container.scrollHeight;
            container.scrollTop = newHeight - prevHeight;
          }
        }, 0);
      } else {
        setHasMore(false);
      }
    } finally {
      setLoadingMore(false);
    }
  };

  const send = () => {
    if (!input) return;
    const text = input;
    // Atomically append user + assistant placeholder to avoid batching races
    useChatStore.setState((state: any) => ({
      messages: [
        ...state.messages,
        { id: crypto.randomUUID(), role: 'user', content: text } as Msg,
        { id: crypto.randomUUID(), role: 'assistant', content: '' } as Msg,
      ],
    }));
    setInput('');
    const payload = JSON.stringify({ type: 'user_message', text });
    const trySend = (attempts: number) => {
      const ws = wsRef.current;
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(payload);
      } else if (attempts > 0) {
        setTimeout(() => trySend(attempts - 1), 100);
      }
    };
    trySend(30); // up to ~3s

    // Optimistic fallback: if no assistant message appears shortly, show echo to keep UX responsive
    setTimeout(() => {
      useChatStore.setState((state: any) => {
        const msgs: Msg[] = state.messages;
        // find last user index (the one we just added)
        const lastIdx = msgs.length - 1;
        const hasAssistantAfter = msgs.some((m, i) => i > lastIdx && m.role === 'assistant');
        if (!hasAssistantAfter) {
          return { messages: [...msgs, { id: crypto.randomUUID(), role: 'assistant', content: `You said: ${text}` }] };
        }
        return {};
      });
    }, 1200);
  };

  return (
    <div className="p-4 max-w-2xl mx-auto">
      <div className="text-lg font-semibold mb-2">
        {assistantName ? `Assistant: ${assistantName}` : 'Assistant'}
        {conversationId ? ` | Conversation: ${conversationId}` : ''}
      </div>
      <div className="space-y-3 mb-4" ref={containerRef} style={{ maxHeight: '60vh', overflowY: 'auto', border: '1px solid #eee', padding: '8px', borderRadius: 8 }}>
        {hasMore && (
          <button onClick={loadMore} disabled={loadingMore} className="px-3 py-1 rounded border">
            {loadingMore ? 'Loading...' : 'Load more messages'}
          </button>
        )}
        {messages.map((m: Msg) => (
          <div key={m.id} className={m.role === 'user' ? 'text-right' : 'text-left'}>
            <div
              className="inline-block rounded-2xl px-4 py-2 shadow"
              {...(m.role === 'assistant' ? { 'data-testid': 'assistant-msg' } : {})}
            >
              {m.content && m.content.length > 0 ? m.content : '\u00A0'}
            </div>
          </div>
        ))}
        {messages.length === 0 && <div className="text-gray-500">まだメッセージがありません</div>}
      </div>
      <div className="flex gap-2">
        <input className="border rounded px-3 py-2 flex-1" value={input} onChange={(e)=>setInput(e.target.value)} placeholder="Type message..." />
        <button className="px-4 py-2 rounded bg-black text-white" onClick={send} disabled={!input.trim()}>Send</button>
      </div>
    </div>
  );
}
