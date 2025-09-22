import { FormEvent, useMemo, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { requestRoutingDecision } from '../api/routing';
import type { RoutingDecision } from '../types/routing';

const formatList = (items: string[]) => (items.length ? items.join(', ') : 'なし');

export default function RoutingDebugPage() {
  const [prompt, setPrompt] = useState('売上データを分析してレポートをまとめて');
  const [assistantId, setAssistantId] = useState('');
  const [conversationId, setConversationId] = useState('');

  const mutation = useMutation({
    mutationFn: requestRoutingDecision,
  });

  const decision = mutation.data;
  const isLoading = mutation.isPending;
  const errorMessage = mutation.error instanceof Error ? mutation.error.message : undefined;

  const sendRequest = (event: FormEvent) => {
    event.preventDefault();
    if (!assistantId || !prompt.trim()) {
      return;
    }
    mutation.mutate({
      prompt,
      assistant_id: assistantId,
      conversation_id: conversationId || undefined,
    });
  };

  const reasoningLines = useMemo(() => {
    if (!decision?.reasoning) return [];
    return decision.reasoning.split('. ').filter(Boolean);
  }, [decision?.reasoning]);

  return (
    <div className="p-6 space-y-6">
      <section>
        <h1 className="text-2xl font-semibold mb-4">Routing Inspector</h1>
        <p className="text-sm text-gray-600">
          プロンプトとアシスタントIDを指定してバックエンドのルーティング判断を確認します。
        </p>
      </section>

      <form onSubmit={sendRequest} className="space-y-4 max-w-3xl">
        <div className="space-y-2">
          <label className="block text-sm font-medium">Prompt</label>
          <textarea
            className="w-full border rounded px-3 py-2"
            rows={4}
            value={prompt}
            onChange={(event) => setPrompt(event.target.value)}
            placeholder="リクエスト内容を入力してください"
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium">Assistant ID</label>
            <input
              className="w-full border rounded px-3 py-2"
              value={assistantId}
              onChange={(event) => setAssistantId(event.target.value)}
              placeholder="UUID"
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium">Conversation ID (任意)</label>
            <input
              className="w-full border rounded px-3 py-2"
              value={conversationId}
              onChange={(event) => setConversationId(event.target.value)}
              placeholder="UUID"
            />
          </div>
        </div>

        <button
          type="submit"
          className="px-4 py-2 rounded bg-black text-white disabled:opacity-60"
          disabled={isLoading || !assistantId || !prompt.trim()}
        >
          {isLoading ? 'Routing...' : 'Route Task'}
        </button>
        {errorMessage && <p className="text-sm text-red-600">{errorMessage}</p>}
      </form>

      {decision && <DecisionPanel decision={decision} reasoningLines={reasoningLines} />}
    </div>
  );
}

function DecisionPanel({
  decision,
  reasoningLines,
}: {
  decision: RoutingDecision;
  reasoningLines: string[];
}) {
  const { llm, agent, skills, analysis, meta } = decision;

  return (
    <section className="border rounded-lg p-5 space-y-6 bg-white shadow-sm">
      <header>
        <h2 className="text-xl font-semibold">Routing Result</h2>
        <p className="text-xs text-gray-500">バックエンドが決定したLLM/エージェント構成</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="font-semibold text-sm text-gray-700">LLM</h3>
          <p className="text-base font-medium">{llm.model}</p>
          {llm.reason && <p className="text-xs text-gray-500">理由: {llm.reason}</p>}
          <p className="text-xs text-gray-500">Fallbacks: {formatList(llm.fallbacks)}</p>
        </div>
        <div>
          <h3 className="font-semibold text-sm text-gray-700">Agent</h3>
          <p className="text-base font-medium">{agent.name}</p>
          {agent.description && <p className="text-xs text-gray-500">{agent.description}</p>}
          <p className="text-xs text-gray-500">Path: {agent.file_path ?? '未設定'}</p>
        </div>
      </div>

      <div>
        <h3 className="font-semibold text-sm text-gray-700">Matched Skills</h3>
        <p className="text-sm">{formatList(skills)}</p>
      </div>

      {reasoningLines.length > 0 && (
        <div>
          <h3 className="font-semibold text-sm text-gray-700">Reasoning</h3>
          <ol className="list-decimal list-inside text-sm space-y-1">
            {reasoningLines.map((line, index) => (
              <li key={index}>{line}</li>
            ))}
          </ol>
        </div>
      )}

      <div>
        <h3 className="font-semibold text-sm text-gray-700">Analyzed Task</h3>
        <div className="text-sm text-gray-700 space-y-1">
          <p>Intent: <span className="font-medium">{analysis.intent}</span> (confidence {analysis.confidence.toFixed(2)})</p>
          <p>Keywords: {formatList(analysis.keywords)}</p>
          {analysis.summary && <p>Summary: {analysis.summary}</p>}
        </div>
      </div>

      <div>
        <h3 className="font-semibold text-sm text-gray-700">Meta</h3>
        {Object.keys(meta).length === 0 ? (
          <p className="text-sm text-gray-500">追加情報なし</p>
        ) : (
          <ul className="text-sm text-gray-700 space-y-1">
            {Object.entries(meta).map(([key, value]) => (
              <li key={key}><span className="font-medium">{key}</span>: {value}</li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
