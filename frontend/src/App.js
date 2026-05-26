import React, { useState } from 'react';
import Feed from './components/Feed';
import Login from './components/Login';
import Create from './components/Create';
import Discover from './components/Discover';
import Profile from './components/Profile';

function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [userId, setUserId] = useState(localStorage.getItem('userId'));
  const [page, setPage] = useState('feed');

  const handleLogin = (newToken, newUserId) => {
    localStorage.setItem('token', newToken);
    localStorage.setItem('userId', newUserId);
    setToken(newToken);
    setUserId(newUserId);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userId');
    setToken(null);
    setUserId(null);
    setPage('feed');
  };

  if (!token) return <div className="bg-gray-100 min-h-screen flex items-center"><Login onLogin={handleLogin} /></div>;

  return (
    <div className="flex h-screen bg-white font-sans text-gray-900">
      
      {/* SIDEBAR GAUCHE (Style Pinterest) */}
      <aside className="w-20 flex flex-col items-center py-6 border-r border-gray-100 space-y-8">
        <div className="text-red-600 text-3xl font-bold mb-4 cursor-pointer" onClick={() => setPage('feed')}>D</div>
        
        <nav className="flex flex-col gap-6 text-2xl text-gray-500">
          <button onClick={() => setPage('feed')} className={`hover:text-black transition-colors ${page === 'feed' ? 'text-black' : ''}`} title="Accueil">🏠</button>
          <button onClick={() => setPage('discover')} className={`hover:text-black transition-colors ${page === 'discover' ? 'text-black' : ''}`} title="Explorer">🧭</button>
          <button onClick={() => setPage('create')} className={`hover:text-black transition-colors ${page === 'create' ? 'text-black' : ''}`} title="Créer">➕</button>
          <button className="hover:text-black" title="Notifications">🔔</button>
          <button className="hover:text-black" title="Messages">💬</button>
        </nav>

        <div className="mt-auto pb-4 flex flex-col gap-6">
          <button onClick={() => setPage('profile')} className="w-10 h-10 bg-amber-200 rounded-full flex items-center justify-center text-sm font-bold border border-gray-200">
            {userId ? "U" : "?"}
          </button>
          <button onClick={handleLogout} className="text-xs font-bold text-gray-400 hover:text-red-500 uppercase">Sortir</button>
        </div>
      </aside>

      {/* ZONE PRINCIPALE (TopBar + Content) */}
      <div className="flex-1 flex flex-col overflow-hidden">
        
        {/* TOP BAR AVEC RECHERCHE */}
        <header className="h-20 flex items-center px-8 gap-4">
          <div className="flex-1 relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">🔍</span>
            <input 
              type="text" 
              placeholder="Rechercher des idées, des créateurs..." 
              className="w-full bg-[#efefef] hover:bg-[#e1e1e1] py-3 pl-12 pr-4 rounded-full outline-none transition-colors"
            />
          </div>
          <div className="flex gap-4">
             <button className="p-2 hover:bg-gray-100 rounded-full text-xl text-gray-600">⚙️</button>
          </div>
        </header>

        {/* CONTENU DÉROULANT */}
        <main className="flex-1 overflow-y-auto px-8 pb-10">
          {page === 'feed'     && <Feed     token={token} />}
          {page === 'discover' && <Discover token={token} />}
          {page === 'create'   && <Create   token={token} />}
          {page === 'profile'  && <Profile  token={token} userId={userId} />}
        </main>
      </div>
    </div>
  );
}

export default App;