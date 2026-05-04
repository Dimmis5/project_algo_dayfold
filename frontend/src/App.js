import React, { useState } from 'react';
import Feed from './components/Feed';
import Login from './components/Login';
import Create from './components/Create';
import Discover from './components/Discover';
import './App.css';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [page, setPage] = useState('feed');

  const handleLogin = (newToken) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setPage('feed');
  };

  return (
    <div className="app">
      <header className="header">
        <h1 className="logo">Dayfold</h1>
        {token && (
          <nav className="nav">
            <button className={`nav-btn ${page === 'feed' ? 'nav-btn-active' : ''}`} onClick={() => setPage('feed')}>Feed</button>
            <button className={`nav-btn ${page === 'discover' ? 'nav-btn-active' : ''}`} onClick={() => setPage('discover')}>Discover</button>
            <button className={`nav-btn ${page === 'create' ? 'nav-btn-active' : ''}`} onClick={() => setPage('create')}>Create</button>
            <button className="logout-btn" onClick={handleLogout}>Logout</button>
          </nav>
        )}
      </header>
      <main>
        {!token && <Login onLogin={handleLogin} />}
        {token && page === 'feed'     && <Feed     token={token} />}
        {token && page === 'discover' && <Discover token={token} />}
        {token && page === 'create'   && <Create   token={token} />}
      </main>
    </div>
  );
}

export default App;