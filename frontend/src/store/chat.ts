import { create } from 'zustand';

type Msg = { id: string; role: 'user'|'assistant'; content: string };

type ChatState = {
  messages: Msg[];
  push: (m: Msg) => void;
  reset: () => void;
};

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  push: (m) => set((s) => ({ messages: [...s.messages, m] })),
  reset: () => set({ messages: [] }),
}));
