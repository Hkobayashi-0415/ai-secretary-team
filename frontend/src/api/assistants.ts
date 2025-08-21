// frontend/src/api/assistants.ts
import apiClient from './client';
import type { Assistant, AssistantCreate } from '../types/assistant';

export const getAssistants = async (): Promise<Assistant[]> => {
  const response = await apiClient.get<Assistant[]>('/assistants');
  return response.data;
};

export const createAssistant = async (data: AssistantCreate): Promise<Assistant> => {
  const response = await apiClient.post<Assistant>('/assistants', data);
  return response.data;
};
