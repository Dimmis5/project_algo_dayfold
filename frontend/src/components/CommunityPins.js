import React, { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

const API = 'http://localhost:8000';

function CommunityPins({ token }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [community, setCommunity] = useState(null);
  const [loading, setLoading] = useState(true);
  const [likedIds, setLikedIds] = useState(new Set());
  const [savedIds, setSavedIds] = useState(new Set());
  const [zoomedPin, setZoomedPin] = useState(null);

  const getImageSrc = (pin) => (
    pin.image_url?.startsWith('http') ? pin.image_url : `${API}${pin.image_url}`
  );

  const fetchCommunity = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/algo/communities/${id}/pins`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setCommunity(res.ok ? data : null);
      setLikedIds(new Set(data.liked_ids || []));
      setSavedIds(new Set(data.saved_ids || []));
    } catch (e) {
      console.error('Community pins failed:', e);
      setCommunity(null);
    } finally {
      setLoading(false);
    }
  }, [id, token]);

  useEffect(() => {
    fetchCommunity();
  }, [fetchCommunity]);

  const likePin = async (e, pinId) => {
    e.stopPropagation();
    const res = await fetch(`${API}/pins/${pinId}/like`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (!res.ok) return;

    setCommunity(prev => ({
      ...prev,
      pins: prev.pins.map(pin => pin.id === pinId ? { ...pin, likes: data.pin.likes } : pin),
    }));
    setLikedIds(prev => {
      const next = new Set(prev);
      data.liked ? next.add(pinId) : next.delete(pinId);
      return next;
    });
  };

  const savePin = async (e, pinId) => {
    e.stopPropagation();
    const res = await fetch(`${API}/pins/${pinId}/save`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
    });
    const data = await res.json();
    if (!res.ok) return;

    setSavedIds(prev => {
      const next = new Set(prev);
      data.saved ? next.add(pinId) : next.delete(pinId);
      return next;
    });
  };

  const sharePin = async (e, pinId) => {
    e.stopPropagation();
    try {
      await navigator.clipboard.writeText(`${window.location.origin}/pin/${pinId}`);
    } catch (error) {
      console.error('Share failed:', error);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[60vh] text-gray-400 italic">
        Loading community pins...
      </div>
    );
  }

  if (!community) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-10">
        <button
          onClick={() => navigate('/discover')}
          className="mb-6 text-sm font-bold text-gray-500 hover:text-black"
        >
          Back to Discover
        </button>
        <div className="py-20 text-center bg-gray-50 rounded-3xl border border-dashed border-gray-200">
          <p className="text-gray-400">Community not found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto px-2 md:px-8 py-8">
      <button
        onClick={() => navigate('/discover')}
        className="mb-6 flex items-center gap-2 text-sm font-bold text-gray-500 hover:text-black"
      >
        <span>&lt;</span>
        Back to communities
      </button>

      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 mb-8">
        <div>
          <h1 className="text-3xl font-black text-gray-900">{community.name}</h1>
          <p className="text-sm text-gray-500 mt-2">
            {community.pins.length} pins posted by {community.members.length} members
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          {community.members.map(member => (
            <button
              key={member.id}
              onClick={() => navigate(`/profile/${member.id}`)}
              className="px-3 py-1.5 bg-gray-50 hover:bg-gray-100 border border-gray-100 rounded-xl text-xs font-bold text-gray-700"
            >
              @{member.username}
            </button>
          ))}
        </div>
      </div>

      {community.pins.length === 0 ? (
        <div className="py-20 text-center bg-gray-50 rounded-3xl border border-dashed border-gray-200">
          <p className="text-gray-400">No pins posted by this community yet.</p>
        </div>
      ) : (
        <div className="columns-2 md:columns-3 lg:columns-4 xl:columns-5 gap-4 space-y-4">
          {community.pins.map(pin => (
            <div
              key={pin.id}
              className="break-inside-avoid group relative mb-4"
            >
              <div
                onClick={() => setZoomedPin(pin)}
                className="relative rounded-[20px] overflow-hidden bg-gray-100 shadow-sm transition-all duration-300 group-hover:shadow-xl border border-gray-100 cursor-zoom-in"
              >
                {pin.image_url ? (
                  <img
                    src={getImageSrc(pin)}
                    alt={pin.title}
                    className="w-full h-auto object-cover transition-transform duration-500 group-hover:scale-105"
                    style={{ minHeight: '150px', maxHeight: '500px' }}
                  />
                ) : (
                  <div className="h-52 flex items-center justify-center bg-gray-200 text-4xl font-black text-white">
                    {pin.title[0]}
                  </div>
                )}

                <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity p-3 flex flex-col justify-between">
                  <div className="flex justify-end">
                    <button
                      onClick={(e) => savePin(e, pin.id)}
                      className={`px-4 py-2 rounded-full font-bold text-xs shadow-lg ${
                        savedIds.has(pin.id) ? 'bg-gray-900 text-white' : 'bg-red-600 text-white hover:bg-red-700'
                      }`}
                    >
                      {savedIds.has(pin.id) ? 'Saved' : 'Save'}
                    </button>
                  </div>
                  <div className="flex justify-end items-center">
                    <button
                      onClick={(e) => sharePin(e, pin.id)}
                      className="bg-white/90 hover:bg-white px-3 py-2 rounded-full shadow-md text-xs font-bold text-gray-800"
                    >
                      Share
                    </button>
                  </div>
                </div>
              </div>

              <div className="mt-2 px-1 flex items-start justify-between gap-2">
                <button
                  onClick={() => navigate(`/pin/${pin.id}`)}
                  className="min-w-0 text-left"
                >
                  <p className="text-sm font-semibold text-gray-900 line-clamp-2">{pin.title}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    By {pin.author} - {pin.category || pin.board_title}
                  </p>
                </button>
                <button
                  onClick={(e) => likePin(e, pin.id)}
                  className="flex items-center gap-1 shrink-0 active:scale-90 transition-transform"
                >
                  <span className={likedIds.has(pin.id) ? 'text-red-500' : 'text-gray-300'}>♥</span>
                  <span className="text-xs font-bold text-gray-600">{pin.likes || 0}</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {zoomedPin && (
        <div
          className="fixed inset-0 z-50 bg-black/80 p-4 md:p-8 flex items-center justify-center"
          onClick={() => setZoomedPin(null)}
        >
          <button
            onClick={() => setZoomedPin(null)}
            className="absolute top-4 right-4 bg-white text-black rounded-full px-4 py-2 text-sm font-black"
          >
            Close
          </button>
          <img
            src={getImageSrc(zoomedPin)}
            alt={zoomedPin.title}
            className="max-h-full max-w-full object-contain rounded-2xl shadow-2xl"
            onClick={e => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
}

export default CommunityPins;
