// frontend/src/api/client.ts
import axios from 'axios';

// バックエンドAPIのベースURLを設定します。
// .envファイルなどから読み込むのが理想ですが、まずは直接記述します。
const rawOrigin = (import.meta as any).env?.VITE_API_URL ?? 'http://localhost:8000';
const trimmed = String(rawOrigin).replace(/\/$/, '');
const API_BASE_URL = trimmed.startsWith('http') ? `${trimmed}/api/v1` : `${trimmed}/v1`;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター（今後の拡張用）
// ここに、リクエストが送信される前にトークンをヘッダーに付与する処理などを追加できます。
apiClient.interceptors.request.use(
  (config) => {
    // const token = localStorage.getItem('accessToken');
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// レスポンスインターセプター（今後の拡張用）
// ここに、エラーレスポンスを共通でハンドリングする処理などを追加できます。
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 例えば、401 Unauthorizedエラーの場合はログインページにリダイレクトするなど
    return Promise.reject(error);
  }
);

export default apiClient;
