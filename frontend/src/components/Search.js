import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const API = 'http://localhost:8000';

function Search({ token }) {
  const [results, setResults] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const query = new URLSearchParams(useLocation().search).get('q');

  useEffect(() => {
    if (!query) return;

    const fetchResults = async () => {
      setLoading(true);
      try {
        const headers = { Authorization: `Bearer ${token}` };
        const [pinsRes, usersRes] = await Promise.all([
          fetch(`${API}/search?q=${encodeURIComponent(query)}`, { headers }),
          fetch(`${API}/users/search?q=${encodeURIComponent(query)}`, { headers }),
        ]);
        const pinsData = await pinsRes.json();
        const usersData = await usersRes.json();
        setResults(Array.isArray(pinsData) ? pinsData : []);
        setUsers(usersData.users || []);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };

    fetchResults();
  }, [query, token]);

  if (loading) {
    return <div className="p-20 text-center text-gray-500 italic">Searching for "{query}"...</div>;
  }

  return (
    <div className="max-w-[1600px] mx-auto px-2 md:px-8">
      <h2 className="text-xl font-bold mb-6 text-gray-700">
        {results.length + users.length} results for "{query}"
      </h2>

      {users.length > 0 && (
        <section className="mb-10">
          <h3 className="text-sm font-black uppercase tracking-widest text-gray-500 mb-4">
            Users
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {users.map(user => (
              <button
                key={user.id}
                onClick={() => navigate(`/profile/${user.id}`)}
                className="flex items-center gap-3 p-4 bg-white border border-gray-100 rounded-2xl hover:bg-gray-50 text-left transition-colors"
              >
                <span className="w-11 h-11 rounded-full bg-red-50 text-red-600 flex items-center justify-center font-black">
                  {user.username[0].toUpperCase()}
                </span>
                <span>
                  <span className="block text-sm font-bold text-gray-900">{user.username}</span>
                  <span className="block text-xs text-gray-400">{user.email}</span>
                </span>
              </button>
            ))}
          </div>
        </section>
      )}

      {results.length === 0 ? (
        <div className="text-center py-20 bg-gray-50 rounded-[40px]">
          <p className="text-gray-400">No pin results found. Try "Art", "Design", or a username like "nina".</p>
        </div>
      ) : (
        <div className="columns-2 md:columns-3 lg:columns-4 xl:columns-5 gap-4 space-y-4">
          {results.map(pin => (
            <div
              key={pin.id}
              onClick={() => navigate(`/pin/${pin.id}`)}
              className="break-inside-avoid mb-4 group relative cursor-pointer"
            >
              <div className="relative rounded-[20px] overflow-hidden bg-gray-100 shadow-sm border border-gray-100">
                {pin.image_url ? (
                  <img
                    src={pin.image_url.startsWith('http') ? pin.image_url : `${API}${pin.image_url}`}
                    className="w-full h-auto object-cover"
                    alt={pin.title}
                  />
                ) : (
                  <div className="w-full h-40 bg-gray-200 flex items-center justify-center text-gray-400 font-bold">
                    {pin.title[0]}
                  </div>
                )}
                <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity p-3 flex flex-col justify-between">
                  <div className="flex justify-end">
                    <button className="bg-red-600 text-white px-4 py-2 rounded-full font-bold text-xs">Save</button>
                  </div>
                </div>
              </div>
              <p className="mt-2 text-sm font-semibold px-1">{pin.title}</p>
              <p className="text-[11px] text-gray-400 px-1 uppercase font-bold">{pin.category}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Search;
