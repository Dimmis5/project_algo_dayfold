import React, { useCallback, useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API = 'http://localhost:8000';

function Friends({ token }) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [results, setResults] = useState([]);
  const [followingIds, setFollowingIds] = useState(new Set());
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const headers = useMemo(() => ({ Authorization: `Bearer ${token}` }), [token]);

  const loadSuggestions = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/users/suggestions`, { headers });
      const data = await res.json();
      setSuggestions(data.suggestions || []);
    } catch (e) {
      console.error('Friend suggestions failed:', e);
    } finally {
      setLoading(false);
    }
  }, [headers]);

  useEffect(() => {
    loadSuggestions();
  }, [loadSuggestions]);

  useEffect(() => {
    const trimmed = query.trim();
    if (!trimmed) {
      setResults([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`${API}/users/search?q=${encodeURIComponent(trimmed)}`, { headers });
        const data = await res.json();
        setResults(data.users || []);
      } catch (e) {
        console.error('Friend search failed:', e);
      }
    }, 180);

    return () => clearTimeout(timer);
  }, [query, headers]);

  const followUser = async (userId) => {
    const res = await fetch(`${API}/users/${userId}/follow`, {
      method: 'POST',
      headers,
    });

    if (res.ok) {
      setFollowingIds(prev => new Set(prev).add(userId));
      setSuggestions(prev => prev.filter(user => user.id !== userId));
    }
  };

  const visibleUsers = query.trim() ? results : suggestions;

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <div className="flex flex-col gap-2 mb-8">
        <h1 className="text-3xl font-black text-gray-900 tracking-tight">Find Friends</h1>
        <p className="text-sm text-gray-500">
          Search by username or email. When the field is empty, Dayfold shows suggested friends.
        </p>
      </div>

      <div className="mb-8">
        <input
          autoFocus
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Search friends..."
          className="w-full bg-[#efefef] hover:bg-[#e2e2e2] focus:bg-white focus:ring-2 focus:ring-red-200 py-4 pl-5 pr-4 rounded-2xl outline-none transition-all text-gray-900"
        />
      </div>

      <div className="flex items-center justify-between mb-4">
        <h2 className="text-sm font-black uppercase tracking-widest text-gray-500">
          {query.trim() ? 'Search results' : 'Suggestions'}
        </h2>
        {!query.trim() && (
          <button
            onClick={loadSuggestions}
            className="text-xs font-bold text-gray-500 hover:text-black"
          >
            Refresh
          </button>
        )}
      </div>

      {loading ? (
        <div className="py-16 text-center text-gray-400 italic">Loading friends...</div>
      ) : visibleUsers.length === 0 ? (
        <div className="py-16 text-center bg-gray-50 rounded-3xl border border-dashed border-gray-200">
          <p className="text-gray-400">No users found.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {visibleUsers.map(user => (
            <div
              key={user.id}
              className="flex items-center justify-between gap-4 p-4 bg-white border border-gray-100 rounded-2xl hover:border-gray-200 transition-colors"
            >
              <button
                onClick={() => navigate(`/profile/${user.id}`)}
                className="flex items-center gap-3 text-left min-w-0"
              >
                <span className="w-12 h-12 rounded-full bg-red-50 text-red-600 flex items-center justify-center font-black shrink-0">
                  {user.username[0].toUpperCase()}
                </span>
                <span className="min-w-0">
                  <span className="block font-bold text-gray-900 truncate">{user.username}</span>
                  <span className="block text-xs text-gray-400 truncate">{user.email}</span>
                </span>
              </button>

              <button
                onClick={() => followUser(user.id)}
                disabled={followingIds.has(user.id)}
                className={`px-4 py-2 rounded-full text-xs font-black transition-colors shrink-0 ${
                  followingIds.has(user.id)
                    ? 'bg-gray-100 text-gray-400'
                    : 'bg-black text-white hover:bg-gray-800'
                }`}
              >
                {followingIds.has(user.id) ? 'FOLLOWING' : 'FOLLOW'}
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Friends;
