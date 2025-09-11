# AI秘書チーム・プラットフォーム - テスト戦略

**作成日**: 2025年8月17日  
**作成者**: 中野五月（Claude Code）  
**バージョン**: 1.0

## 🧪 テスト戦略概要

### テストピラミッド
```
        ┌─────────────┐
        │   E2E Tests │  ← 少数・高価値
        └─────────────┘
      ┌─────────────────┐
      │ Integration     │  ← 中程度・中価値
      │ Tests           │
      └─────────────────┘
    ┌─────────────────────┐
    │   Unit Tests        │  ← 多数・低価値
    └─────────────────────┘
```

### テストカバレッジ目標
- **Unit Tests**: 90%以上
- **Integration Tests**: 80%以上
- **E2E Tests**: 主要フロー100%

## 🔧 テスト環境設定

### バックエンドテスト環境

#### テスト用データベース設定
```python
# tests/conftest.py
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.models import Base
from app.core.database import get_async_db

# テスト用データベースURL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    """テスト用のイベントループ"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """テスト用データベースセッション"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    TestingSessionLocal = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with TestingSessionLocal() as session:
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(test_db):
    """テスト用クライアント"""
    from fastapi.testclient import TestClient
    from app.main import app
    
    def override_get_db():
        return test_db
    
    app.dependency_overrides[get_async_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
```

#### テスト用設定
```python
# tests/test_config.py
import pytest
from app.core.config import Settings

@pytest.fixture
def test_settings():
    """テスト用設定"""
    return Settings(
        database_url="sqlite+aiosqlite:///./test.db",
        redis_url="redis://localhost:6379",
        gemini_api_key="test_api_key",
        environment="test",
        debug=True
    )
```

### フロントエンドテスト環境

#### Vitest設定
```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.d.ts',
        '**/*.config.*',
        '**/coverage/**'
      ]
    }
  }
});
```

#### テストセットアップ
```typescript
// src/test/setup.ts
import { vi } from 'vitest';
import '@testing-library/jest-dom';

// MSWの設定
import { setupServer } from 'msw/node';
import { handlers } from './mocks/handlers';

const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// グローバルモック
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));
```

## 🔬 ユニットテスト

### バックエンドユニットテスト

#### モデルテスト
```python
# tests/models/test_models.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import User, AIAssistant

@pytest.mark.asyncio
async def test_user_creation(test_db: AsyncSession):
    """ユーザー作成テスト"""
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.is_active is True

@pytest.mark.asyncio
async def test_assistant_creation(test_db: AsyncSession):
    """アシスタント作成テスト"""
    # ユーザーを作成
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    test_db.add(user)
    await test_db.commit()
    
    # アシスタントを作成
    assistant = AIAssistant(
        user_id=user.id,
        name="Test Assistant",
        description="Test Description",
        default_llm_model="gemini-pro"
    )
    test_db.add(assistant)
    await test_db.commit()
    await test_db.refresh(assistant)
    
    assert assistant.id is not None
    assert assistant.name == "Test Assistant"
    assert assistant.user_id == user.id
    assert assistant.is_active is True
```

#### サービステスト
```python
# tests/services/test_routing.py
import pytest
from unittest.mock import AsyncMock, patch
from app.services.routing.orchestrator import RoutingOrchestrator
from app.services.routing.core.task_analyzer import TaskAnalyzer
from app.services.routing.core.skill_matcher import SkillMatcher

@pytest.mark.asyncio
async def test_routing_orchestrator():
    """ルーティングオーケストレーターのテスト"""
    orchestrator = RoutingOrchestrator()
    
    # モックの設定
    with patch.object(TaskAnalyzer, 'analyze') as mock_analyze, \
         patch.object(SkillMatcher, 'match_skills') as mock_match, \
         patch.object(orchestrator.agent_selector, 'select_agent') as mock_select, \
         patch.object(orchestrator.llm_router, 'route_to_agent') as mock_route:
        
        # モックの戻り値設定
        mock_analyze.return_value = {"type": "analysis", "complexity": "medium"}
        mock_match.return_value = ["analysis", "research"]
        mock_select.return_value = "assistant_1"
        mock_route.return_value = "AI response"
        
        # テスト実行
        result = await orchestrator.route_request("Test prompt")
        
        # アサーション
        assert result == "AI response"
        mock_analyze.assert_called_once_with("Test prompt")
        mock_match.assert_called_once()
        mock_select.assert_called_once()
        mock_route.assert_called_once()
```

#### APIエンドポイントテスト
```python
# tests/api/test_assistants.py
import pytest
from fastapi.testclient import TestClient
from app.models.models import User, AIAssistant

@pytest.mark.asyncio
async def test_create_assistant(client: TestClient, test_db: AsyncSession):
    """アシスタント作成APIテスト"""
    # テストデータの準備
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    test_db.add(user)
    await test_db.commit()
    
    # リクエストデータ
    assistant_data = {
        "name": "Test Assistant",
        "description": "Test Description",
        "default_llm_model": "gemini-pro"
    }
    
    # API呼び出し
    response = client.post("/api/v1/assistants/", json=assistant_data)
    
    # アサーション
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Assistant"
    assert data["description"] == "Test Description"
    assert data["is_active"] is True

@pytest.mark.asyncio
async def test_get_assistants(client: TestClient, test_db: AsyncSession):
    """アシスタント一覧取得APIテスト"""
    # テストデータの準備
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    test_db.add(user)
    await test_db.commit()
    
    assistant1 = AIAssistant(
        user_id=user.id,
        name="Assistant 1",
        description="Description 1"
    )
    assistant2 = AIAssistant(
        user_id=user.id,
        name="Assistant 2",
        description="Description 2"
    )
    test_db.add_all([assistant1, assistant2])
    await test_db.commit()
    
    # API呼び出し
    response = client.get("/api/v1/assistants/")
    
    # アサーション
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] in ["Assistant 1", "Assistant 2"]
    assert data[1]["name"] in ["Assistant 1", "Assistant 2"]
```

### フロントエンドユニットテスト

#### コンポーネントテスト
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

  it('renders user menu', () => {
    renderWithRouter(<Header />);
    expect(screen.getByText('User')).toBeInTheDocument();
  });
});
```

#### ページコンポーネントテスト
```typescript
// src/pages/__tests__/AssistantsPage.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AssistantsPage } from '../AssistantsPage';
import { server } from '../../test/mocks/server';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('AssistantsPage', () => {
  beforeEach(() => {
    server.use(
      rest.get('/api/v1/assistants', (req, res, ctx) => {
        return res(ctx.json([
          {
            id: '1',
            name: 'Test Assistant 1',
            description: 'Test Description 1',
            is_active: true
          }
        ]));
      })
    );
  });

  it('renders assistant list', async () => {
    renderWithQueryClient(<AssistantsPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Assistant 1')).toBeInTheDocument();
    });
  });

  it('creates new assistant', async () => {
    server.use(
      rest.post('/api/v1/assistants', (req, res, ctx) => {
        return res(ctx.json({
          id: '2',
          name: 'New Assistant',
          description: 'New Description',
          is_active: true
        }));
      })
    );

    renderWithQueryClient(<AssistantsPage />);
    
    // フォーム入力
    fireEvent.change(screen.getByLabelText('Name:'), {
      target: { value: 'New Assistant' }
    });
    fireEvent.change(screen.getByLabelText('Description:'), {
      target: { value: 'New Description' }
    });
    
    // 送信
    fireEvent.click(screen.getByText('Create Assistant'));
    
    await waitFor(() => {
      expect(screen.getByText('New Assistant')).toBeInTheDocument();
    });
  });
});
```

#### カスタムフックテスト
```typescript
// src/hooks/__tests__/useAssistants.test.ts
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useAssistants } from '../useAssistants';
import { server } from '../../test/mocks/server';

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => {
  const queryClient = createTestQueryClient();
  return (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  );
};

describe('useAssistants', () => {
  it('fetches assistants successfully', async () => {
    server.use(
      rest.get('/api/v1/assistants', (req, res, ctx) => {
        return res(ctx.json([
          {
            id: '1',
            name: 'Test Assistant',
            description: 'Test Description',
            is_active: true
          }
        ]));
      })
    );

    const { result } = renderHook(() => useAssistants(), { wrapper });

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.data).toHaveLength(1);
    expect(result.current.data[0].name).toBe('Test Assistant');
  });

  it('handles error state', async () => {
    server.use(
      rest.get('/api/v1/assistants', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    const { result } = renderHook(() => useAssistants(), { wrapper });

    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });
  });
});
```

## 🔗 統合テスト

### バックエンド統合テスト

#### データベース統合テスト
```python
# tests/integration/test_database.py
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.models import User, AIAssistant, Conversation, Message

@pytest.mark.asyncio
async def test_user_assistant_relationship(test_db: AsyncSession):
    """ユーザーとアシスタントの関係性テスト"""
    # ユーザー作成
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    test_db.add(user)
    await test_db.commit()
    await test_db.refresh(user)
    
    # アシスタント作成
    assistant = AIAssistant(
        user_id=user.id,
        name="Test Assistant",
        description="Test Description"
    )
    test_db.add(assistant)
    await test_db.commit()
    await test_db.refresh(assistant)
    
    # 関係性の確認
    assert assistant.user_id == user.id
    assert assistant in user.assistants

@pytest.mark.asyncio
async def test_conversation_message_relationship(test_db: AsyncSession):
    """会話とメッセージの関係性テスト"""
    # ユーザーとアシスタントの作成
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    test_db.add(user)
    await test_db.commit()
    
    assistant = AIAssistant(
        user_id=user.id,
        name="Test Assistant"
    )
    test_db.add(assistant)
    await test_db.commit()
    
    # 会話作成
    conversation = Conversation(
        user_id=user.id,
        assistant_id=assistant.id,
        title="Test Conversation"
    )
    test_db.add(conversation)
    await test_db.commit()
    await test_db.refresh(conversation)
    
    # メッセージ作成
    message1 = Message(
        conversation_id=conversation.id,
        role="user",
        content="Hello"
    )
    message2 = Message(
        conversation_id=conversation.id,
        role="assistant",
        content="Hi there!"
    )
    test_db.add_all([message1, message2])
    await test_db.commit()
    
    # 関係性の確認
    assert len(conversation.messages) == 2
    assert message1.conversation_id == conversation.id
    assert message2.conversation_id == conversation.id
```

#### API統合テスト
```python
# tests/integration/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from app.models.models import User, AIAssistant

@pytest.mark.asyncio
async def test_assistant_crud_flow(client: TestClient, test_db: AsyncSession):
    """アシスタントCRUDフローの統合テスト"""
    # ユーザー作成
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hashed_password"
    )
    test_db.add(user)
    await test_db.commit()
    
    # 1. アシスタント作成
    create_data = {
        "name": "Test Assistant",
        "description": "Test Description",
        "default_llm_model": "gemini-pro"
    }
    create_response = client.post("/api/v1/assistants/", json=create_data)
    assert create_response.status_code == 201
    created_assistant = create_response.json()
    assistant_id = created_assistant["id"]
    
    # 2. アシスタント一覧取得
    list_response = client.get("/api/v1/assistants/")
    assert list_response.status_code == 200
    assistants = list_response.json()
    assert len(assistants) == 1
    assert assistants[0]["name"] == "Test Assistant"
    
    # 3. アシスタント詳細取得
    detail_response = client.get(f"/api/v1/assistants/{assistant_id}")
    assert detail_response.status_code == 200
    assistant_detail = detail_response.json()
    assert assistant_detail["name"] == "Test Assistant"
    
    # 4. アシスタント更新
    update_data = {
        "name": "Updated Assistant",
        "description": "Updated Description"
    }
    update_response = client.put(f"/api/v1/assistants/{assistant_id}", json=update_data)
    assert update_response.status_code == 200
    updated_assistant = update_response.json()
    assert updated_assistant["name"] == "Updated Assistant"
    
    # 5. アシスタント削除
    delete_response = client.delete(f"/api/v1/assistants/{assistant_id}")
    assert delete_response.status_code == 204
    
    # 6. 削除確認
    get_after_delete = client.get(f"/api/v1/assistants/{assistant_id}")
    assert get_after_delete.status_code == 404
```

### フロントエンド統合テスト

#### API統合テスト
```typescript
// src/api/__tests__/assistants.test.ts
import { rest } from 'msw';
import { server } from '../../test/mocks/server';
import { getAssistants, createAssistant, updateAssistant, deleteAssistant } from '../assistants';

describe('Assistants API', () => {
  it('fetches assistants', async () => {
    const mockAssistants = [
      {
        id: '1',
        name: 'Test Assistant 1',
        description: 'Description 1',
        is_active: true
      }
    ];

    server.use(
      rest.get('/api/v1/assistants', (req, res, ctx) => {
        return res(ctx.json(mockAssistants));
      })
    );

    const result = await getAssistants();
    expect(result).toEqual(mockAssistants);
  });

  it('creates assistant', async () => {
    const newAssistant = {
      name: 'New Assistant',
      description: 'New Description'
    };

    const createdAssistant = {
      id: '2',
      ...newAssistant,
      is_active: true
    };

    server.use(
      rest.post('/api/v1/assistants', (req, res, ctx) => {
        return res(ctx.json(createdAssistant));
      })
    );

    const result = await createAssistant(newAssistant);
    expect(result).toEqual(createdAssistant);
  });

  it('handles API errors', async () => {
    server.use(
      rest.get('/api/v1/assistants', (req, res, ctx) => {
        return res(ctx.status(500));
      })
    );

    await expect(getAssistants()).rejects.toThrow();
  });
});
```

## 🎭 E2Eテスト

### Playwright設定

#### Playwright設定ファイル
```typescript
// playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },
  ],
  webServer: {
    command: 'npm run dev',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
  },
});
```

#### E2Eテスト例
```typescript
// e2e/assistants.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Assistants Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/assistants');
  });

  test('should display assistants page', async ({ page }) => {
    await expect(page.getByText('AI Assistants Management')).toBeVisible();
    await expect(page.getByText('Create New Assistant')).toBeVisible();
  });

  test('should create new assistant', async ({ page }) => {
    // フォーム入力
    await page.fill('input[id="name"]', 'Test Assistant');
    await page.fill('input[id="description"]', 'Test Description');
    
    // 送信
    await page.click('button[type="submit"]');
    
    // 確認
    await expect(page.getByText('Test Assistant')).toBeVisible();
    await expect(page.getByText('Test Description')).toBeVisible();
  });

  test('should display existing assistants', async ({ page }) => {
    // モックデータの設定（MSWを使用）
    await page.route('**/api/v1/assistants', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          {
            id: '1',
            name: 'Existing Assistant',
            description: 'Existing Description',
            is_active: true
          }
        ])
      });
    });

    await page.reload();
    await expect(page.getByText('Existing Assistant')).toBeVisible();
  });

  test('should handle form validation', async ({ page }) => {
    // 空のフォームで送信
    await page.click('button[type="submit"]');
    
    // バリデーションエラーの確認
    await expect(page.getByText('Name is required')).toBeVisible();
  });
});
```

#### 会話機能のE2Eテスト
```typescript
// e2e/conversation.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Conversation Flow', () => {
  test('should start conversation with assistant', async ({ page }) => {
    await page.goto('/');
    
    // アシスタント選択
    await page.click('[data-testid="assistant-select"]');
    await page.click('[data-testid="assistant-option-1"]');
    
    // メッセージ送信
    await page.fill('[data-testid="message-input"]', 'Hello, how are you?');
    await page.click('[data-testid="send-button"]');
    
    // メッセージ表示確認
    await expect(page.getByText('Hello, how are you?')).toBeVisible();
    
    // AI応答の確認（モック）
    await expect(page.getByText('I am doing well, thank you!')).toBeVisible();
  });

  test('should handle file upload', async ({ page }) => {
    await page.goto('/conversation/1');
    
    // ファイルアップロード
    const fileInput = page.locator('input[type="file"]');
    await fileInput.setInputFiles('test-files/sample.pdf');
    
    // アップロード完了の確認
    await expect(page.getByText('sample.pdf uploaded successfully')).toBeVisible();
  });
});
```

## 📊 テストカバレッジ

### カバレッジ設定

#### バックエンドカバレッジ
```bash
# pytest-covを使用
pytest --cov=app --cov-report=html --cov-report=term-missing
```

#### フロントエンドカバレッジ
```bash
# Vitestのカバレッジ
npm run test:coverage
```

### カバレッジレポート例
```
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
app/__init__.py             0      0   100%
app/main.py                15      0   100%
app/api/__init__.py         0      0   100%
app/api/v1/api.py          10      0   100%
app/api/v1/endpoints/assistants.py  45      2    96%   23, 45
app/core/config.py         25      0   100%
app/core/database.py       20      0   100%
app/models/models.py       50      0   100%
app/schemas/assistant.py   30      0   100%
app/services/__init__.py    0      0   100%
------------------------------------------------------
TOTAL                     195      2    99%
```

## 🚀 テスト自動化

### GitHub Actions設定

#### テストワークフロー
```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install pytest-cov
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml --cov-report=html
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run tests
      run: |
        cd frontend
        npm run test:coverage
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./frontend/coverage/lcov.info

  e2e-tests:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Install Playwright Browsers
      run: |
        cd frontend
        npx playwright install --with-deps
    
    - name: Run E2E tests
      run: |
        cd frontend
        npm run test:e2e
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report
        path: frontend/playwright-report/
```

## 🔧 テストデータ管理

### テストデータファクトリー

#### バックエンドファクトリー
```python
# tests/factories.py
import factory
from app.models.models import User, AIAssistant, Conversation, Message

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session_persistence = "commit"
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password_hash = "hashed_password"
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_verified = True

class AIAssistantFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = AIAssistant
        sqlalchemy_session_persistence = "commit"
    
    user = factory.SubFactory(UserFactory)
    name = factory.Faker("name")
    description = factory.Faker("text", max_nb_chars=200)
    default_llm_model = "gemini-pro"
    is_active = True
    is_public = False

class ConversationFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Conversation
        sqlalchemy_session_persistence = "commit"
    
    user = factory.SubFactory(UserFactory)
    assistant = factory.SubFactory(AIAssistantFactory)
    title = factory.Faker("sentence", nb_words=4)
    conversation_type = "chat"
    status = "active"

class MessageFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Message
        sqlalchemy_session_persistence = "commit"
    
    conversation = factory.SubFactory(ConversationFactory)
    role = factory.Iterator(["user", "assistant"])
    content = factory.Faker("text", max_nb_chars=500)
    content_type = "text"
```

#### フロントエンドファクトリー
```typescript
// src/test/factories.ts
import { faker } from '@faker-js/faker';

export const createUser = (overrides = {}) => ({
  id: faker.string.uuid(),
  username: faker.internet.userName(),
  email: faker.internet.email(),
  first_name: faker.person.firstName(),
  last_name: faker.person.lastName(),
  is_active: true,
  is_verified: true,
  created_at: faker.date.past().toISOString(),
  updated_at: faker.date.recent().toISOString(),
  ...overrides
});

export const createAssistant = (overrides = {}) => ({
  id: faker.string.uuid(),
  user_id: faker.string.uuid(),
  name: faker.person.fullName(),
  description: faker.lorem.sentence(),
  personality_template_id: faker.string.uuid(),
  voice_id: faker.string.uuid(),
  avatar_id: faker.string.uuid(),
  default_llm_model: 'gemini-pro',
  custom_system_prompt: faker.lorem.paragraph(),
  is_active: true,
  is_public: false,
  created_at: faker.date.past().toISOString(),
  updated_at: faker.date.recent().toISOString(),
  ...overrides
});

export const createConversation = (overrides = {}) => ({
  id: faker.string.uuid(),
  user_id: faker.string.uuid(),
  assistant_id: faker.string.uuid(),
  title: faker.lorem.sentence(),
  conversation_type: 'chat',
  status: 'active',
  voice_enabled: false,
  voice_id: null,
  metadata: {},
  started_at: faker.date.past().toISOString(),
  ended_at: null,
  created_at: faker.date.past().toISOString(),
  updated_at: faker.date.recent().toISOString(),
  ...overrides
});

export const createMessage = (overrides = {}) => ({
  id: faker.string.uuid(),
  conversation_id: faker.string.uuid(),
  role: faker.helpers.arrayElement(['user', 'assistant']),
  content: faker.lorem.sentence(),
  content_type: 'text',
  parent_id: null,
  metadata: {},
  created_at: faker.date.past().toISOString(),
  ...overrides
});
```

## 📈 パフォーマンステスト

### 負荷テスト

#### Locust設定
```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class AISecretaryUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """ログイン処理"""
        self.client.post("/api/v1/auth/login", json={
            "username": "testuser",
            "password": "testpassword"
        })
    
    @task(3)
    def get_assistants(self):
        """アシスタント一覧取得"""
        self.client.get("/api/v1/assistants/")
    
    @task(2)
    def create_assistant(self):
        """アシスタント作成"""
        self.client.post("/api/v1/assistants/", json={
            "name": "Test Assistant",
            "description": "Test Description"
        })
    
    @task(1)
    def send_message(self):
        """メッセージ送信"""
        self.client.post("/api/v1/conversations/1/messages", json={
            "role": "user",
            "content": "Hello, how are you?"
        })
```

#### 実行コマンド
```bash
# 負荷テスト実行
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# ヘッドレスモード
locust -f tests/performance/locustfile.py --host=http://localhost:8000 \
  --users=100 --spawn-rate=10 --run-time=60s --headless
```

このテスト戦略により、高品質で信頼性の高いアプリケーションを構築できます。
