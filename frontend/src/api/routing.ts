import apiClient from './client';
import type { RoutingDecision, RoutingRequest } from '../types/routing';

export const requestRoutingDecision = async (
  payload: RoutingRequest,
): Promise<RoutingDecision> => {
  const response = await apiClient.post<RoutingDecision>('/routing/route', payload);
  return response.data;
};
