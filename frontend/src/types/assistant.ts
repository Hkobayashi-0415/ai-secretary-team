// frontend/src/types/assistant.ts
import { z } from 'zod';

// Zodスキーマでバリデーションルールを定義
export const AssistantSchema = z.object({
  id: z.string().uuid(),
  user_id: z.string().uuid(),
  name: z.string().min(1, "名前は必須です").max(100),
  description: z.string().optional(),
  default_llm_model: z.string().optional(),
});

export const AssistantCreateSchema = AssistantSchema.omit({ id: true, user_id: true });

// TypeScriptの型を生成
export type Assistant = z.infer<typeof AssistantSchema>;
export type AssistantCreate = z.infer<typeof AssistantCreateSchema>;