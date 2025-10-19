// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route,} from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import AssistantsPage from './pages/AssistantsPage';
import ConversationsPage from './pages/ConversationsPage';
import ChatPage from './pages/ChatPage';

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
            <Route path="/conversations" element={<ConversationsPage />} />
            {/* <Route path="*" element={<NotFoundPage />} /> 
              将来的に「v7_relativeSplatPath」の警告に対応するために、
              このような「*」を使ったルートも考慮に入れておくと良いですね。
            */}
            <Route path="/chat/:conversationId" element={<ChatPage />} />
          </Routes>
        </Layout>
      </Router>

    </QueryClientProvider>
  );
};

export default App;
