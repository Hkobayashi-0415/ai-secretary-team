// frontend/src/api/client.ts
import axios from "axios";

// Docker/E2E では same-origin で叩けるよう相対パスが安全
export const API_BASE_URL =
  (import.meta as any).env?.VITE_API_URL
    ? `${(import.meta as any).env.VITE_API_URL}/api/v1`
    : "/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

export default apiClient;
