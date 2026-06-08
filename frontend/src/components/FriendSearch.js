import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function FriendSearch({ token }) {
  const [query, setQuery] = useState('');
  const [friends, setFriends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [followingId, setFollowingId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const controller = new AbortController();

    const fetchFriends = async () => {
      setLoading(true);
      try {
        const params = new URLSearchParams({ q: query });
        const res = await fetch(`${API}/users/search/friends?${params}`, {
          headers: { Authorization: `Bearer ${token}` },
          signal: controller.signal
        });
        const data = await res.json();
        setFriends(Array.isArray(data) ? data : []);
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.error('Friend search error:', error);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };

    const timer = setTimeout(fetchFriends, 250);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [query, token]);

  const handleFollow = async (userId) => {
    setFollowingId(userId);
    try {
      const res = await fetch(`${API}/users/${userId}/follow`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        setFriends(prev => prev.map(friend => (
          friend.id === userId
            ? { ...friend, is_following: true, followers: Number(friend.followers) + 1 }
            : friend
        )));
      }
    } catch (error) {
      console.error('Follow error:', error);
    } finally {
      setFollowingId(null);
    }
  };

  return (
    <div className="max-w-5xl mx-auto px-2 md:px-8 py-4">
      <div className="mb-8">
        <h1 className="text-3xl font-black tracking-tight text-gray-900">Recherche d'ami</h1>
        <div className="mt-5 relative">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="11" cy="11" r="8" />
              <path d="m21 21-4.3-4.3" />
            </svg>
          </span>
          <input
            type="text"
            placeholder="Chercher un pseudo ou un email"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-[#efefef] hover:bg-[#e2e2e2] focus:bg-white focus:ring-2 focus:ring-red-100 py-3 pl-12 pr-4 rounded-full outline-none transition-all"
          />
        </div>
      </div>

      {loading ? (
        <div className="py-16 text-center text-gray-500 font-medium italic">Recherche en cours...</div>
      ) : friends.length === 0 ? (
        <div className="py-16 text-center bg-gray-50 rounded-3xl border border-gray-100">
          <p className="text-gray-500 font-medium">Aucun utilisateur trouve.</p>
        </div>
      ) : (
        <div className="grid gap-3">
          {friends.map(friend => (
            <div
              key={friend.id}
              className="flex items-center gap-4 rounded-2xl border border-gray-100 bg-white p-4 shadow-sm hover:shadow-md transition-shadow"
            >
              <button
                onClick={() => navigate(`/profile/${friend.id}`)}
                className="w-14 h-14 rounded-full bg-gray-100 border border-gray-200 flex items-center justify-center text-xl font-black text-gray-700 shrink-0"
                title={`Voir le profil de ${friend.username}`}
              >
                {friend.username[0].toUpperCase()}
              </button>

              <button
                onClick={() => navigate(`/profile/${friend.id}`)}
                className="min-w-0 flex-1 text-left"
              >
                <div className="flex items-center gap-2">
                  <p className="font-bold text-gray-900 truncate">{friend.username}</p>
                  {friend.is_admin && (
                    <span className="px-2 py-0.5 bg-gray-800 text-white text-[10px] font-black rounded uppercase">
                      Admin
                    </span>
                  )}
                </div>
                <p className="text-sm text-gray-500 truncate">{friend.email}</p>
                <p className="text-xs font-semibold text-gray-400 mt-1">
                  {friend.followers} followers · {friend.boards_count} boards
                </p>
              </button>

              <button
                onClick={() => handleFollow(friend.id)}
                disabled={friend.is_following || followingId === friend.id}
                className={`px-5 py-2.5 rounded-full font-bold text-sm transition-all active:scale-95 ${
                  friend.is_following
                    ? 'bg-gray-100 text-gray-500 cursor-default'
                    : 'bg-red-600 text-white hover:bg-red-700 shadow-md'
                }`}
              >
                {followingId === friend.id ? '...' : friend.is_following ? 'Suivi' : 'Suivre'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default FriendSearch;
