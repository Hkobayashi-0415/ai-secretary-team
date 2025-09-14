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
        <NavLink to="/" end>Dashboard</NavLink>
        <NavLink to="/assistants">AI Assistants</NavLink>
        {/* <NavLink to="/projects">Projects</NavLink> */}
        {/* <NavLink to="/workflows">Workflows</NavLink> */}
      </nav>
      <div className="user-menu">
        <span>User</span>
      </div>
    </header>
  );
};

export default Header;
