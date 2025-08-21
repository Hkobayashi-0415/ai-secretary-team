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