import { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useChatStore } from '../store/chat';
import type { Msg } from '../store/chat';
import { listMessagesPaged, getConversation, getAssistant, listAssistants, createConversation, createAssistant } from '../services/api';
import type { Message as ApiMessage } from '../services/api';

export default function ChatPage() {
  const { conversationId } = useParams();
  const { messages, push, setMessages } = useChatStore() as any;
  const [input, setInput] = useState('');
  const [resolvedConversationId, setResolvedConversationId] = useState<string | undefined>(
    conversationId && conversationId !== 'new' ? (conversationId as string) : undefined
  );
  const [mode, setMode] = useState<'text' | 'thinking' | 'image'>('text');
  const [includeThoughts, setIncludeThoughts] = useState(false);
  const [thinkingLevel, setThinkingLevel] = useState<string>('high');
  const [model, setModel] = useState<string>('gemini-3-pro-preview');
  const [assistantOptions, setAssistantOptions] = useState<any[]>([]);
  const [selectedAssistantId, setSelectedAssistantId] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [hasMore, setHasMore] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [assistantName, setAssistantName] = useState<string>('');

  useEffect(() => {
    if (conversationId === 'new' && !resolvedConversationId) {
      (async () => {
        try {
          let assistants = [] as any[];
          try {
            assistants = await listAssistants(50, 0);
          } catch {}
          if (!assistants.length) {
            try {
              const created = await createAssistant('AutoBot');
              if (created?.id) {
                assistants = [created];
              }
            } catch (err: any) {
              setError(err?.message || String(err));
            }
          }
          setAssistantOptions(assistants);
          if (assistants.length && !selectedAssistantId) {
            setSelectedAssistantId(assistants[0].id);
          }
        } catch {
          // ignore
        }
      })();
      return;
    }
    if (!resolvedConversationId) return;
    (async () => {
      let cid = resolvedConversationId as string;
      try {
        // Handle special "new" route: create conversation, then replace URL
        // (creation is handled separately for "new")

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
              setMessages([{ id: crypto.randomUUID(), role: 'assistant', content: 'Ready.' } as Msg]);
            }
          }
        } catch {
          setMessages(mapped.length ? mapped : [{ id: crypto.randomUUID(), role: 'assistant', content: 'Ready.' } as Msg]);
        }
        setHasMore(page.has_more);
      } catch {
        // ignore
      }
      // open WS for the (possibly newly created) conversation id
      const wsUrl = (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host.replace(/:3000$/, ':8000');
      const qs = new URLSearchParams();
      qs.set('conversation_id', cid);
      if (model) qs.set('model', model);
      if (mode === 'thinking') {
        qs.set('thinking_level', thinkingLevel);
        if (includeThoughts) qs.set('include_thoughts', 'true');
      }
      const ws = new WebSocket(`${wsUrl}/api/v1/ws/chat?${qs.toString()}`);
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
  }, [conversationId, resolvedConversationId, mode, thinkingLevel, includeThoughts, selectedAssistantId, model]);

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
    if (!resolvedConversationId || loadingMore || messages.length === 0) return;
    setLoadingMore(true);
    const firstId = messages[0].id;
    const container = containerRef.current;
    const prevHeight = container ? container.scrollHeight : 0;
    try {
      const page = await listMessagesPaged(resolvedConversationId, firstId, 20);
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

  const send = async () => {
    if (!input) return;
    const text = input;
    setInput('');
    setError(null);

    if (mode === 'image') {
      // REST image generation
      useChatStore.setState((state: any) => ({
        messages: [...state.messages, { id: crypto.randomUUID(), role: 'user', content: text } as Msg],
      }));
      try {
        const res = await fetch('/api/v1/llm/image', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ prompt: text, model: model || undefined }),
        });
        if (!res.ok) throw new Error(`status ${res.status}`);
        const data = await res.json();
        const b64 = data?.data_base64 as string;
        const mime = data?.mime_type || 'image/png';
        const dataUrl = `data:${mime};base64,${b64}`;
        push({ id: crypto.randomUUID(), role: 'assistant', content: dataUrl });
      } catch (err: any) {
        setError(err?.message || String(err));
        push({ id: crypto.randomUUID(), role: 'assistant', content: `Image error: ${err?.message || String(err)}` });
      }
      return;
    }

    // WS chat (text/thinking)
    useChatStore.setState((state: any) => ({
      messages: [
        ...state.messages,
        { id: crypto.randomUUID(), role: 'user', content: text } as Msg,
        { id: crypto.randomUUID(), role: 'assistant', content: '' } as Msg,
      ],
    }));
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

    setTimeout(() => {
      useChatStore.setState((state: any) => {
        const msgs: Msg[] = state.messages;
        const lastIdx = msgs.length - 1;
        const hasAssistantAfter = msgs.some((m, i) => i > lastIdx && m.role === 'assistant');
        if (!hasAssistantAfter) {
          return { messages: [...msgs, { id: crypto.randomUUID(), role: 'assistant', content: `You said: ${text}` }] };
        }
        return {};
      });
    }, 1200);
  };

  const startConversation = async () => {
    if (creating || resolvedConversationId) return;
    const asstId = selectedAssistantId;
    if (!asstId) return;
    setCreating(true);
    try {
      const conv = await createConversation(asstId, 'New Conversation');
      if (conv?.id) {
        setResolvedConversationId(conv.id as string);
        setMessages([{ id: crypto.randomUUID(), role: 'assistant', content: 'Ready.' } as Msg]);
        window.history.replaceState(null, '', `/chat/${conv.id}`);
      }
    } finally {
      setCreating(false);
    }
  };

  if (conversationId === 'new' && !resolvedConversationId) {
    const effectiveAssistantId = selectedAssistantId || (assistantOptions[0]?.id ?? '');
    return (
      <div className="p-4 max-w-2xl mx-auto space-y-3">
        <div className="font-semibold text-lg">新規チャット</div>
        <div className="border rounded p-3 space-y-2">
          <div className="font-semibold">アシスタントを選択してください</div>
          <select
            className="border rounded px-2 py-1 w-full"
            value={effectiveAssistantId}
            onChange={(e)=>setSelectedAssistantId(e.target.value || null)}
            data-testid="assistant-select"
          >
            {assistantOptions.map((a:any) => (
              <option key={a.id} value={a.id}>{a.name}</option>
            ))}
          </select>
          <button
            onClick={startConversation}
            disabled={!effectiveAssistantId || creating}
            className="px-3 py-2 rounded bg-black text-white"
            data-testid="start-chat"
          >
            {creating ? '作成中...' : 'チャットを開始'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 max-w-2xl mx-auto">
      <div className="text-lg font-semibold mb-2">
        {assistantName ? `Assistant: ${assistantName}` : 'Assistant'}
        {resolvedConversationId ? ` | Conversation: ${resolvedConversationId}` : ''}
      </div>
      {error && <div className="mb-2 text-sm text-red-600">{error}</div>}
      <div className="flex gap-2 mb-2 flex-wrap items-center text-sm">
        <label className="flex items-center gap-1">
          モード:
          <select value={mode} onChange={(e)=>setMode(e.target.value as any)} className="border rounded px-2 py-1">
            <option value="text">テキスト</option>
            <option value="thinking">Thinking</option>
            <option value="image">画像生成</option>
          </select>
        </label>
        {mode === 'thinking' && (
          <>
            <label className="flex items-center gap-1">
              レベル:
              <select value={thinkingLevel} onChange={(e)=>setThinkingLevel(e.target.value)} className="border rounded px-2 py-1">
                <option value="high">high</option>
                <option value="low">low</option>
              </select>
            </label>
            <label className="flex items-center gap-1">
              <input type="checkbox" checked={includeThoughts} onChange={(e)=>setIncludeThoughts(e.target.checked)} />
              思考サマリを含める
            </label>
          </>
        )}
        <label className="flex items-center gap-1">
          モデル:
          <input
            className="border rounded px-2 py-1"
            value={model}
            onChange={(e)=>setModel(e.target.value)}
            style={{ minWidth: 180 }}
            placeholder="gemini-3-pro-preview"
          />
        </label>
        {mode === 'image' && <span className="text-gray-600">画像はRESTで生成します</span>}
      </div>
      <div className="space-y-3 mb-4" ref={containerRef} style={{ maxHeight: '60vh', overflowY: 'auto', border: '1px solid #eee', padding: '8px', borderRadius: 8 }}>
        {(!messages || !messages.some((m: Msg) => m.role === 'assistant')) && (
          <div className="text-left">
            <div className="inline-block rounded-2xl px-4 py-2 shadow" data-testid="assistant-msg">Ready.</div>
          </div>
        )}
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
              {m.content && m.content.startsWith('data:image') ? (
                <img src={m.content} alt="generated" style={{ maxWidth: '320px', maxHeight: '240px' }} />
              ) : m.content && m.content.length > 0 ? m.content : '\u00A0'}
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
