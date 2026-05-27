import React, { useState } from 'react';
import { Routes, Route, NavLink, Navigate, useNavigate } from 'react-router-dom';
import Feed from './components/Feed';
import Login from './components/Login';
import Create from './components/Create';
import Discover from './components/Discover';
import Profile from './components/Profile';
import Search from './components/Search'; 

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [userId, setUserId] = useState(localStorage.getItem('userId'));
  const [searchInput, setSearchInput] = useState('');
  const navigate = useNavigate();

  const handleLogin = (newToken, newUserId) => {
    localStorage.setItem('token', newToken);
    localStorage.setItem('userId', newUserId);
    setToken(newToken);
    setUserId(newUserId);
    navigate('/feed');
  };

  const handleLogout = () => {
    localStorage.clear();
    setToken(null);
    setUserId(null);
    navigate('/');
  };

  const handleSearchSubmit = (e) => {
    if (e.key === 'Enter' && searchInput.trim() !== '') {
      navigate(`/search?q=${searchInput}`);
    }
  };

  if (!token) return <Login onLogin={handleLogin} />;

  return (
    <div className="flex h-screen bg-white font-sans text-gray-900">
      
      <aside className="w-20 flex flex-col items-center py-6 border-r border-gray-100 space-y-8">
        <NavLink to="/feed" className="text-red-600 text-3xl font-bold mb-4">D</NavLink>
        
        <nav className="flex flex-col gap-6 text-2xl text-gray-400">
          <NavLink to="/feed" className={({ isActive }) => isActive ? "text-black" : "hover:text-black"}>🏠</NavLink>
          <NavLink to="/discover" className={({ isActive }) => isActive ? "text-black" : "hover:text-black"}>🧭</NavLink>
          <NavLink to="/create" className={({ isActive }) => isActive ? "text-black" : "hover:text-black"}>➕</NavLink>
        </nav>

        <div className="mt-auto pb-4 flex flex-col gap-6 items-center">
          <NavLink 
            to={`/profile/${userId}`} 
            className={({ isActive }) => `w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold border ${isActive ? 'border-black bg-gray-200' : 'border-gray-200 bg-amber-100'}`}
          >
            U
          </NavLink>
          <button onClick={handleLogout} className="text-[10px] font-black text-gray-400 hover:text-red-500 uppercase">Sortir</button>
        </div>
      </aside>

      <div className="flex-1 flex flex-col overflow-hidden">
        
        <header className="h-20 flex items-center px-8 gap-4">
          <div className="flex-1 relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
            <input 
              type="text" 
              placeholder="Rechercher des idées..." 
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              onKeyDown={handleSearchSubmit}
              className="w-full bg-[#efefef] hover:bg-[#e2e2e2] py-3 pl-12 pr-4 rounded-full outline-none transition-colors"
            />
          </div>
        </header>

        <main className="flex-1 overflow-y-auto px-8 pb-10">
          <Routes>
            <Route path="/feed" element={<Feed token={token} />} />
            <Route path="/discover" element={<Discover token={token} />} />
            <Route path="/create" element={<Create token={token} />} />
            <Route path="/search" element={<Search token={token} />} />
            <Route path="/profile/:id" element={<Profile token={token} userId={userId} />} />
            <Route path="*" element={<Navigate to="/feed" />} />
          </Routes>
        </main>
      </div>
    </div>
  );
}

export default App;