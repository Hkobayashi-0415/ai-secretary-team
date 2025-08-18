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