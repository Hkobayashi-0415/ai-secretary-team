// frontend/src/components/Header.tsx
import React from 'react';
import { Link, NavLink } from 'react-router-dom';

const Header: React.FC = () => {
  return (
    <header className="header">
      <div className="logo">
        <Link to="/">AI Secretary Team</Link>
      </div>
      <nav className="navigation" style={{ display: 'flex', gap: '1rem' }}>
        {/* まずは動く2つだけ。Projects/Workflowsはページが出来たら有効化 */}
        <NavLink to="/" end>Dashboard</NavLink>
        {/* <NavLink to="/projects">Projects</NavLink> */}
        {/* <NavLink to="/workflows">Workflows</NavLink> */}
        <NavLink to="/assistants">AI Assistants</NavLink>
      </nav>
      <div className="user-menu">
        <span>User</span>
      </div>
    </header>
  );
};

export default Header;
