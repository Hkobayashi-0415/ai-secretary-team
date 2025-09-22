export type ConversationTurn = {
  role: string;
  content: string;
  message_id?: string | null;
  created_at?: string | null;
};

export type AnalyzedTask = {
  keywords: string[];
  intent: string;
  confidence: number;
  assistant_id?: string | null;
  conversation_id?: string | null;
  history: ConversationTurn[];
  summary?: string | null;
  primary_skill?: string | null;
};

export type LLMSelection = {
  model: string;
  fallbacks: string[];
  reason?: string | null;
};

export type AgentSelection = {
  id: string;
  name: string;
  description?: string | null;
  file_path?: string | null;
  tags: string[];
  score?: number | null;
};

export type RoutingDecision = {
  llm: LLMSelection;
  agent: AgentSelection;
  skills: string[];
  reasoning?: string | null;
  analysis: AnalyzedTask;
  meta: Record<string, string>;
};

export type RoutingRequest = {
  prompt: string;
  assistant_id: string;
  conversation_id?: string | null;
};
