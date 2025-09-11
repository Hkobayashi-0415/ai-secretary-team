# AI秘書チーム・プラットフォーム - フロントエンドアーキテクチャ

**作成日**: 2025年8月17日  
**作成者**: 中野五月（Claude Code）  
**バージョン**: 1.0

## 🏗️ アーキテクチャ概要

### 技術スタック
- **フレームワーク**: React 18.2.0
- **言語**: TypeScript
- **ビルドツール**: Vite 7.1.2
- **スタイリング**: Tailwind CSS
- **UIコンポーネント**: Shadcn UI
- **状態管理**: Zustand 4.4.7
- **データフェッチング**: React Query 5.8.4
- **ルーティング**: React Router DOM 6.20.1

### アーキテクチャパターン
- **コンポーネント指向設計**
- **カスタムフックによるロジック分離**
- **型安全なAPI通信**
- **レスポンシブデザイン**

## 📁 ディレクトリ構造

```
frontend/
├── src/
│   ├── components/            # 再利用可能なUIコンポーネント
│   │   ├── Header.tsx        # ヘッダーコンポーネント
│   │   ├── Layout.tsx        # レイアウトコンポーネント
│   │   └── Sidebar.tsx       # サイドバーコンポーネント
│   ├── pages/                # ページコンポーネント
│   │   └── AssistantsPage.tsx # アシスタント管理ページ
│   ├── api/                  # API通信層
│   │   ├── client.ts         # APIクライアント設定
│   │   └── assistants.ts     # アシスタントAPI
│   ├── types/                # TypeScript型定義
│   │   └── assistant.ts      # アシスタント型定義
│   ├── hooks/                # カスタムフック
│   ├── stores/               # 状態管理ストア
│   ├── utils/                # ユーティリティ関数
│   ├── App.tsx               # メインアプリケーション
│   ├── main.tsx              # エントリーポイント
│   └── index.css             # グローバルスタイル
├── public/                   # 静的ファイル
│   └── react.svg
├── package.json              # 依存関係
├── tsconfig.json             # TypeScript設定
├── vite.config.ts            # Vite設定
└── Dockerfile*               # Docker設定
```

## 🔧 コアコンポーネント

### 1. アプリケーションエントリーポイント (App.tsx)

```typescript
// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import AssistantsPage from './pages/AssistantsPage';

const queryClient = new QueryClient();

const HomePage: React.FC = () => (
  <div>
    <h1>Welcome to AI Secretary Team Platform!</h1>
    <p>This is the main content area.</p>
  </div>
);

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <Router future={{ 
        v7_startTransition: true,
        v7_relativeSplatPath: true 
      }}>
        <Layout>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/assistants" element={<AssistantsPage />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
};

export default App;
```

### 2. レイアウトコンポーネント (components/Layout.tsx)

```typescript
// frontend/src/components/Layout.tsx
import React from 'react';
import Header from './Header';
import Sidebar from './Sidebar';

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <div className="app-container">
      <Header />
      <div className="main-wrapper">
        <Sidebar />
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;
```

### 3. ヘッダーコンポーネント (components/Header.tsx)

```typescript
// frontend/src/components/Header.tsx
import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="logo">AI Secretary Team</div>
      <nav className="navigation">
        <a href="#dashboard">Dashboard</a>
        <a href="#projects">Projects</a>
        <a href="#workflows">Workflows</a>
      </nav>
      <div className="user-menu">
        <span>User</span>
      </div>
    </header>
  );
};

export default Header;
```

### 4. サイドバーコンポーネント (components/Sidebar.tsx)

```typescript
// frontend/src/components/Sidebar.tsx
import React from 'react';

const Sidebar: React.FC = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-menu">
        <p>Menu</p>
        <ul>
          <li>Dashboard</li>
          <li>Projects</li>
          <li>Workflows</li>
          <li>AI Assistants</li>
          <li>Settings</li>
        </ul>
      </div>
    </aside>
  );
};

export default Sidebar;
```

## 📄 ページコンポーネント

### アシスタント管理ページ (pages/AssistantsPage.tsx)

```typescript
// frontend/src/pages/AssistantsPage.tsx
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getAssistants, createAssistant } from '../api/assistants';
import type { AssistantCreate } from '../types/assistant';

const AssistantsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');

  const { data: assistants, isLoading, error } = useQuery({
    queryKey: ['assistants'],
    queryFn: getAssistants,
  });

  const createMutation = useMutation({
    mutationFn: createAssistant,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assistants'] });
      setName('');
      setDescription('');
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const newAssistant: AssistantCreate = { name, description };
    createMutation.mutate(newAssistant);
  };

  return (
    <div>
      <h2>AI Assistants Management</h2>
      
      <form onSubmit={handleSubmit} style={{ marginBottom: '2rem' }}>
        <h3>Create New Assistant</h3>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="name">Name: </label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <label htmlFor="description">Description: </label>
          <input
            id="description"
            type="text"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>
        <button type="submit" disabled={createMutation.isPending}>
          {createMutation.isPending ? 'Creating...' : 'Create Assistant'}
        </button>
        {createMutation.isError && <p>Error creating assistant.</p>}
      </form>

      <h3>Existing Assistants</h3>
      {isLoading && <p>Loading assistants...</p>}
      {error && <p>Error fetching assistants.</p>}
      <ul>
        {assistants?.map((assistant) => (
          <li key={assistant.id}>
            <strong>{assistant.name}</strong>: {assistant.description || 'No description'}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AssistantsPage;
```

## 🔌 API通信層

### 1. APIクライアント設定 (api/client.ts)

```typescript
// frontend/src/api/client.ts
import axios from 'axios';

// バックエンドAPIのベースURLを設定します。
const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// リクエストインターセプター（今後の拡張用）
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
```

### 2. アシスタントAPI (api/assistants.ts)

```typescript
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

export const updateAssistant = async (id: string, data: Partial<AssistantCreate>): Promise<Assistant> => {
  const response = await apiClient.put<Assistant>(`/assistants/${id}`, data);
  return response.data;
};

export const deleteAssistant = async (id: string): Promise<void> => {
  await apiClient.delete(`/assistants/${id}`);
};
```

## 🎨 型定義

### アシスタント型定義 (types/assistant.ts)

```typescript
// frontend/src/types/assistant.ts
export interface Assistant {
  id: string;
  user_id: string;
  name: string;
  description?: string;
  personality_template_id?: string;
  voice_id?: string;
  avatar_id?: string;
  default_llm_model?: string;
  custom_system_prompt?: string;
  is_active: boolean;
  is_public: boolean;
  created_at: string;
  updated_at: string;
}

export interface AssistantCreate {
  name: string;
  description?: string;
  personality_template_id?: string;
  voice_id?: string;
  avatar_id?: string;
  default_llm_model?: string;
  custom_system_prompt?: string;
}

export interface AssistantUpdate {
  name?: string;
  description?: string;
  personality_template_id?: string;
  voice_id?: string;
  avatar_id?: string;
  default_llm_model?: string;
  custom_system_prompt?: string;
}
```

## 🎨 スタイリング

### 1. グローバルスタイル (index.css)

```css
/* frontend/src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* アプリケーション全体のレイアウト */
.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.main-wrapper {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.main-content {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
}

/* ヘッダースタイル */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.logo {
  font-size: 1.5rem;
  font-weight: bold;
  color: #495057;
}

.navigation {
  display: flex;
  gap: 1rem;
}

.navigation a {
  color: #6c757d;
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
}

.navigation a:hover {
  background-color: #e9ecef;
}

/* サイドバースタイル */
.sidebar {
  width: 250px;
  background-color: #f8f9fa;
  border-right: 1px solid #e9ecef;
  padding: 1rem;
}

.sidebar-menu ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.sidebar-menu li {
  padding: 0.5rem 0;
  cursor: pointer;
  color: #6c757d;
  transition: color 0.2s;
}

.sidebar-menu li:hover {
  color: #495057;
}
```

### 2. Tailwind CSS設定

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        secondary: {
          50: '#f8fafc',
          500: '#64748b',
          600: '#475569',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
```

## 🔄 状態管理

### 1. Zustandストア例

```typescript
// stores/assistantStore.ts
import { create } from 'zustand';
import { Assistant } from '../types/assistant';

interface AssistantState {
  assistants: Assistant[];
  selectedAssistant: Assistant | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setAssistants: (assistants: Assistant[]) => void;
  setSelectedAssistant: (assistant: Assistant | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  addAssistant: (assistant: Assistant) => void;
  updateAssistant: (id: string, updates: Partial<Assistant>) => void;
  removeAssistant: (id: string) => void;
}

export const useAssistantStore = create<AssistantState>((set) => ({
  assistants: [],
  selectedAssistant: null,
  isLoading: false,
  error: null,
  
  setAssistants: (assistants) => set({ assistants }),
  setSelectedAssistant: (assistant) => set({ selectedAssistant: assistant }),
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),
  
  addAssistant: (assistant) => set((state) => ({
    assistants: [...state.assistants, assistant]
  })),
  
  updateAssistant: (id, updates) => set((state) => ({
    assistants: state.assistants.map(assistant =>
      assistant.id === id ? { ...assistant, ...updates } : assistant
    )
  })),
  
  removeAssistant: (id) => set((state) => ({
    assistants: state.assistants.filter(assistant => assistant.id !== id)
  })),
}));
```

## 🧪 テスト戦略

### 1. テスト設定

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
  },
});
```

### 2. コンポーネントテスト例

```typescript
// src/components/__tests__/Header.test.tsx
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Header from '../Header';

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Header Component', () => {
  it('renders the logo', () => {
    renderWithRouter(<Header />);
    expect(screen.getByText('AI Secretary Team')).toBeInTheDocument();
  });

  it('renders navigation links', () => {
    renderWithRouter(<Header />);
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Projects')).toBeInTheDocument();
    expect(screen.getByText('Workflows')).toBeInTheDocument();
  });
});
```

## 🚀 ビルド・デプロイ

### 1. Vite設定

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  define: {
    'process.env': process.env,
  },
});
```

### 2. Docker設定

```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3. 環境変数

```bash
# .env
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE=AI Secretary Team Platform
VITE_APP_VERSION=1.0.0
```

## 📱 レスポンシブデザイン

### 1. ブレークポイント

```css
/* レスポンシブデザインのブレークポイント */
@media (max-width: 768px) {
  .main-wrapper {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
  }
  
  .header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .navigation {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .main-content {
    padding: 0.5rem;
  }
  
  .header {
    padding: 0.5rem;
  }
}
```

### 2. モバイル最適化

```typescript
// hooks/useResponsive.ts
import { useState, useEffect } from 'react';

export const useResponsive = () => {
  const [isMobile, setIsMobile] = useState(false);
  const [isTablet, setIsTablet] = useState(false);

  useEffect(() => {
    const checkScreenSize = () => {
      setIsMobile(window.innerWidth < 768);
      setIsTablet(window.innerWidth >= 768 && window.innerWidth < 1024);
    };

    checkScreenSize();
    window.addEventListener('resize', checkScreenSize);

    return () => window.removeEventListener('resize', checkScreenSize);
  }, []);

  return { isMobile, isTablet };
};
```

## 🔒 セキュリティ

### 1. 入力検証

```typescript
// utils/validation.ts
import { z } from 'zod';

export const assistantSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name too long'),
  description: z.string().max(500, 'Description too long').optional(),
  default_llm_model: z.string().max(100, 'Model name too long').optional(),
});

export type AssistantFormData = z.infer<typeof assistantSchema>;
```

### 2. XSS対策

```typescript
// utils/sanitize.ts
import DOMPurify from 'dompurify';

export const sanitizeHtml = (html: string): string => {
  return DOMPurify.sanitize(html);
};

export const sanitizeInput = (input: string): string => {
  return input.replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '');
};
```

## 📊 パフォーマンス最適化

### 1. コード分割

```typescript
// 遅延読み込み
const AssistantsPage = lazy(() => import('./pages/AssistantsPage'));
const DashboardPage = lazy(() => import('./pages/DashboardPage'));

// ルーターでの使用
<Route path="/assistants" element={
  <Suspense fallback={<div>Loading...</div>}>
    <AssistantsPage />
  </Suspense>
} />
```

### 2. メモ化

```typescript
// コンポーネントのメモ化
const AssistantCard = memo(({ assistant }: { assistant: Assistant }) => {
  return (
    <div className="assistant-card">
      <h3>{assistant.name}</h3>
      <p>{assistant.description}</p>
    </div>
  );
});

// コールバックのメモ化
const handleSubmit = useCallback((data: AssistantCreate) => {
  createMutation.mutate(data);
}, [createMutation]);
```

### 3. 仮想化

```typescript
// 大量のリストの仮想化
import { FixedSizeList as List } from 'react-window';

const VirtualizedAssistantList = ({ assistants }: { assistants: Assistant[] }) => {
  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => (
    <div style={style}>
      <AssistantCard assistant={assistants[index]} />
    </div>
  );

  return (
    <List
      height={600}
      itemCount={assistants.length}
      itemSize={120}
    >
      {Row}
    </List>
  );
};
```
