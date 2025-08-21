// frontend/src/App.tsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
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
      <Router>
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