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