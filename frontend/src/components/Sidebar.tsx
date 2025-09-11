// frontend/src/components/Sidebar.tsx
import React from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const itemStyle: React.CSSProperties = { display: 'block', padding: '0.25rem 0' };
  return (
    <aside className="sidebar">
      <div className="sidebar-menu">
        <p>Menu</p>
        <ul style={{ listStyle: 'none', paddingLeft: 0 }}>
          <li><NavLink to="/" end style={itemStyle}>Dashboard</NavLink></li>
          {/* <li><NavLink to="/projects" style={itemStyle}>Projects</NavLink></li> */}
          {/* <li><NavLink to="/workflows" style={itemStyle}>Workflows</NavLink></li> */}
          <li><NavLink to="/assistants" style={itemStyle}>AI Assistants</NavLink></li>
          {/* <li><NavLink to="/settings" style={itemStyle}>Settings</NavLink></li> */}
        </ul>
      </div>
    </aside>
  );
};

export default Sidebar;
