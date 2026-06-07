import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router-dom';

const API = 'http://localhost:8000';

function Feed({ token }) {
  const [pins, setPins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [likedIds, setLikedIds] = useState(new Set());
  const [savedIds, setSavedIds] = useState(new Set());
  const [savingId, setSavingId] = useState(null);
  const observerRef = useRef(null);
  const sentinelRef = useRef(null);
  const navigate = useNavigate();

  const fetchPage = useCallback(async (pageNum) => {
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const res = await fetch(`${API}/algo/feed?page=${pageNum}`, { headers });
      const data = await res.json();
      return data;
    } catch (error) {
      console.error("Feed error:", error);
      return null;
    }
  }, [token]);

  useEffect(() => {
    const init = async () => {
      setLoading(true);
      const data = await fetchPage(1);
      if (data) {
        setPins(data.feed || []);
        setLikedIds(new Set(data.liked_ids || []));
        setHasMore(data.has_more ?? true);
      }
      
      try {
        const userId = localStorage.getItem('userId');
        const res = await fetch(`${API}/users/${userId}/saved`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        const savedData = await res.json();
        setSavedIds(new Set(savedData.saved_pins.map(p => p.id)));
      } catch (e) {
        console.error("Error fetching saved pins:", e);
      }

      setLoading(false);
    };
    init();
  }, [fetchPage, token]);

  useEffect(() => {
    if (observerRef.current) observerRef.current.disconnect();

    observerRef.current = new IntersectionObserver(
      async (entries) => {
        if (entries[0].isIntersecting && hasMore && !loadingMore) {
          setLoadingMore(true);
          const nextPage = page + 1;
          const data = await fetchPage(nextPage);
          if (data && data.feed?.length > 0) {
            setPins(prev => {
              const existingIds = new Set(prev.map(p => p.id));
              const newPins = data.feed.filter(p => !existingIds.has(p.id));
              return [...prev, ...newPins];
            });
            setPage(nextPage);
            setHasMore(data.has_more ?? false);
          } else {
            setHasMore(false);
          }
          setLoadingMore(false);
        }
      },
      { threshold: 0.1 }
    );

    if (sentinelRef.current) observerRef.current.observe(sentinelRef.current);
    return () => observerRef.current?.disconnect();
  }, [hasMore, loadingMore, page, fetchPage]);

  const handleLike = async (e, pinId) => {
    e.stopPropagation();
    try {
      const res = await fetch(`${API}/pins/${pinId}/like`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      const data = await res.json();
      setPins(prev => prev.map(p => p.id === pinId ? { ...p, likes: data.pin.likes } : p));
      setLikedIds(prev => {
        const next = new Set(prev);
        data.liked ? next.add(pinId) : next.delete(pinId);
        return next;
      });
    } catch (error) {
      console.error("Like error:", error);
    }
  };

  const handleSave = async (e, pinId) => {
    e.stopPropagation();
    const isAlreadySaved = savedIds.has(pinId);
    
    setSavingId(pinId);
    try {
      const method = isAlreadySaved ? 'DELETE' : 'POST';
      const res = await fetch(`${API}/pins/${pinId}/save`, {
        method: method,
        headers: { Authorization: `Bearer ${token}` }
      });

      if (res.ok) {
        setSavedIds(prev => {
          const next = new Set(prev);
          if (isAlreadySaved) next.delete(pinId);
          else next.add(pinId);
          return next;
        });
      }
    } catch (error) {
      console.error("Save error:", error);
    } finally {
      setSavingId(null);
    }
  };

  if (loading) return (
    <div className="flex justify-center items-center min-h-[50vh]">
      <div className="flex gap-2">
        <div className="w-3 h-3 bg-red-600 rounded-full animate-bounce"></div>
        <div className="w-3 h-3 bg-red-600 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-3 h-3 bg-red-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
      </div>
    </div>
  );

  return (
    <div className="max-w-[1600px] mx-auto px-2 md:px-8">


      {pins.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 bg-gray-50 rounded-[40px] border-2 border-dashed border-gray-200">
          <div className="text-6xl mb-4">🎨</div>
          <h2 className="text-2xl font-bold text-gray-800">Your feed is empty</h2>
          <p className="text-gray-500 mt-2 text-center max-w-md px-6">
            Explore new creators or create your first board to start the Dayfold adventure.
          </p>
        </div>
      ) : (
        <>
          <div className="columns-2 md:columns-3 lg:columns-4 xl:columns-5 gap-4 space-y-4">
            {pins.map(pin => (
              <div
                key={pin.id}
                onClick={() => navigate(`/pin/${pin.id}`)}
                className="break-inside-avoid group cursor-zoom-in relative mb-4"
              >
                <div className="relative rounded-[20px] overflow-hidden bg-gray-100 shadow-sm transition-all duration-300 group-hover:shadow-xl border border-gray-100">
                    {pin.feed_type && (
                      <span className={`absolute top-2 left-2 text-[10px] font-black px-2 py-0.5 rounded-full uppercase tracking-wider z-10 ${
                        pin.feed_type === 'followed'  ? 'bg-blue-500 text-white' :
                        pin.feed_type === 'discovery' ? 'bg-emerald-500 text-white' :
                                                        'bg-purple-500 text-white'
                      }`}>
                        {pin.feed_type === 'followed'  ? '👥 Following' :
                        pin.feed_type === 'discovery' ? '✦ Discovery' :
                                                        '🎲 Surprise'}
                      </span>
                    )}
                  {pin.image_url ? (
                    <img
                      src={pin.image_url.startsWith('http') ? pin.image_url : `${API}${pin.image_url}`}
                      alt={pin.title}
                      className="w-full h-auto object-cover transition-transform duration-500 group-hover:scale-105"
                      style={{ minHeight: '150px', maxHeight: '500px' }}
                      onError={(e) => { e.target.style.display = 'none'; }}
                    />
                  ) : (
                    <div
                      className={`w-full flex items-center justify-center text-white font-black text-5xl bg-gradient-to-br ${getRandomColor()}`}
                      style={{ height: getRandomHeight() }}
                    >
                      <span className="opacity-40 group-hover:scale-110 transition-transform duration-500">
                        {pin.title[0]}
                      </span>
                    </div>
                  )}

                  <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 p-3 flex flex-col justify-between">
                    <div className="flex justify-end">
                      <button 
                        onClick={(e) => handleSave(e, pin.id)}
                        disabled={savingId === pin.id}
                        className={`${
                          savedIds.has(pin.id) ? 'bg-black' : 'bg-red-600 hover:bg-red-700'
                        } text-white px-5 py-2.5 rounded-full font-bold text-sm shadow-lg transform translate-y-[-10px] group-hover:translate-y-0 transition-all duration-300 disabled:opacity-80`}
                      >
                        {savingId === pin.id ? 'Saving...' : savedIds.has(pin.id) ? 'Saved' : 'Save'}
                      </button>
                    </div>
                    <div className="flex justify-between items-center">
                      <button
                        onClick={(e) => e.stopPropagation()}
                        className="bg-white/90 hover:bg-white p-2 rounded-full shadow-md text-gray-800 transition-colors"
                      >...</button>
                    </div>
                  </div>
                </div>

                <div className="mt-2 px-1 flex items-start justify-between">
                  <div>
                    <p className="text-sm font-semibold text-gray-900 line-clamp-2 leading-tight">{pin.title}</p>
                    <p className="text-xs text-gray-500 mt-1 font-medium italic">
                      {pin.author ? `By ${pin.author}` : `Pin #${pin.id}`}
                    </p>
                  </div>
                  <button
                    onClick={(e) => handleLike(e, pin.id)}
                    className="flex items-center gap-1 group/like active:scale-90 transition-transform"
                  >
                    <span className={`transition-all group-hover/like:scale-125 ${likedIds.has(pin.id) ? 'text-red-500' : 'text-gray-300'}`}>
                      ♥
                    </span>
                    <span className="text-xs font-bold text-gray-600">{pin.likes}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>

          <div ref={sentinelRef} className="h-10 mt-4" />

          {loadingMore && (
            <div className="flex justify-center py-8">
              <div className="flex gap-2">
                <div className="w-3 h-3 bg-red-600 rounded-full animate-bounce"></div>
                <div className="w-3 h-3 bg-red-600 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
                <div className="w-3 h-3 bg-red-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
              </div>
            </div>
          )}

          {!hasMore && pins.length > 0 && (
            <div className="text-center py-10 text-gray-400 text-sm italic">
            </div>
          )}
        </>
      )}
    </div>
  );
}

const getRandomHeight = () => {
  const heights = ['200px', '280px', '350px', '240px', '400px'];
  return heights[Math.floor(Math.random() * heights.length)];
};

const getRandomColor = () => {
  const colors = [
    'from-pink-400 to-rose-500',
    'from-orange-300 to-amber-500',
    'from-indigo-400 to-cyan-500',
    'from-emerald-400 to-teal-500',
    'from-violet-400 to-purple-500'
  ];
  return colors[Math.floor(Math.random() * colors.length)];
};

export default Feed;