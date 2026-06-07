import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';

const API = 'http://localhost:8000';

function PinDetail({ token }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [pin, setPin] = useState(null);
  const [related, setRelated] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [saving, setSaving] = useState(false);

  const fetchPin = useCallback(async () => {
    setLoading(true);
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const [pinRes, relatedRes] = await Promise.all([
        fetch(`${API}/pins/${id}`, { headers }),
        fetch(`${API}/pins/${id}/related`, { headers }),
      ]);
      const pinData = await pinRes.json();
      const relatedData = await relatedRes.json();
      setPin(pinData);
      setRelated(relatedData.related || []);

      // Check if saved
      const userId = localStorage.getItem('userId');
      const savedRes = await fetch(`${API}/users/${userId}/saved`, { headers });
      const savedData = await savedRes.json();
      const saved = savedData.saved_pins.some(p => String(p.id) === String(id));
      setIsSaved(saved);

    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [id, token]);

  useEffect(() => { fetchPin(); }, [fetchPin]);

  const handleLike = async () => {
    const headers = { Authorization: `Bearer ${token}` }; 
    const res = await fetch(`${API}/pins/${id}/like`, { method: 'POST', headers });
    const data = await res.json();
    setPin(prev => ({ ...prev, likes: data.pin.likes }));
  };

  const handleSave = async (e, pinId) => {
    if (e) e.stopPropagation();
    const targetId = pinId || id;
    const isTargetAlreadySaved = pinId ? false : isSaved; // Simplified for related pins

    setSaving(true);
    try {
      const method = (pinId ? false : isSaved) ? 'DELETE' : 'POST';
      const res = await fetch(`${API}/pins/${targetId}/save`, {
        method: method,
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        if (!pinId) setIsSaved(!isSaved);
        else {
            alert(method === 'POST' ? "Enregistré !" : "Retiré !");
        }
      }
    } catch (error) {
      console.error("Save error:", error);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return (
    <div className="flex justify-center items-center min-h-[60vh]">
      <div className="flex gap-2">
        <div className="w-3 h-3 bg-red-600 rounded-full animate-bounce"></div>
        <div className="w-3 h-3 bg-red-600 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
        <div className="w-3 h-3 bg-red-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
      </div>
    </div>
  );

  if (!pin) return <div className="text-center py-20 text-gray-400">Pin not found.</div>;

  const imgSrc = pin.image_url?.startsWith('http') ? pin.image_url : `${API}${pin.image_url}`;

  return (
    <div className="max-w-[1200px] mx-auto px-4 py-6">

      <button
        onClick={() => navigate(-1)}
        className="mb-6 flex items-center gap-2 text-gray-500 hover:text-black transition-colors font-medium text-sm"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        Back
      </button>

      <div className="bg-white rounded-[32px] shadow-2xl overflow-hidden flex flex-col md:flex-row max-w-4xl mx-auto mb-16">

        <div className="md:w-1/2 bg-gray-100 flex items-center justify-center min-h-[400px]">
          {pin.image_url ? (
            <img
              src={imgSrc}
              alt={pin.title}
              className="w-full h-full object-cover"
              style={{ maxHeight: '600px' }}
            />
          ) : (
            <div className="w-full h-full min-h-[400px] bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center">
              <span className="text-6xl font-black text-white opacity-40">{pin.title[0]}</span>
            </div>
          )}
        </div>

        <div className="md:w-1/2 p-8 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-6">
              <button
                onClick={handleLike}
                className="flex items-center gap-2 text-gray-600 hover:text-red-500 transition-colors group"
              >
                <span className="text-2xl group-hover:scale-125 transition-transform">♥</span>
                <span className="font-bold text-sm">{pin.likes}</span>
              </button>
              <button 
                onClick={() => handleSave()}
                disabled={saving}
                className={`${isSaved ? 'bg-black' : 'bg-red-600 hover:bg-red-700'} text-white px-6 py-2.5 rounded-full font-bold text-sm transition-colors shadow-md disabled:opacity-80`}
              >
                {saving ? 'Saving...' : isSaved ? 'Saved' : 'Save'}
              </button>
            </div>

            <h1 className="text-2xl font-black text-gray-900 mb-2 leading-tight">{pin.title}</h1>

            {pin.category && (
              <span className="inline-block bg-gray-100 text-gray-600 text-xs font-bold px-3 py-1 rounded-full mb-4">
                {pin.category}
              </span>
            )}

            {pin.board_title && (
              <p className="text-sm text-gray-500 mb-6">
                Board : <span className="font-semibold text-gray-800">{pin.board_title}</span>
              </p>
            )}
          </div>

          {pin.author && (
            <Link
              to={`/profile/${pin.author_id}`}
              className="flex items-center gap-3 group mt-auto"
            >
              <div className="w-10 h-10 rounded-full bg-amber-100 border border-gray-200 flex items-center justify-center font-bold text-sm text-gray-700 group-hover:border-black transition-colors">
                {pin.author[0].toUpperCase()}
              </div>
              <div>
                <p className="font-bold text-sm text-gray-900 group-hover:underline">{pin.author}</p>
                <p className="text-xs text-gray-400">View profile</p>
              </div>
            </Link>
          )}
        </div>
      </div>

      {related.length > 0 && (
        <div>
          <h2 className="text-xl font-black text-gray-900 mb-6 text-center">More like this</h2>
          <div className="columns-2 md:columns-3 lg:columns-4 xl:columns-5 gap-4 space-y-4">
            {related.map(p => (
              <div
                key={p.id}
                className="break-inside-avoid group cursor-pointer mb-4"
                onClick={() => navigate(`/pin/${p.id}`)}
              >
                <div className="relative rounded-[20px] overflow-hidden bg-gray-100 shadow-sm transition-all duration-300 group-hover:shadow-xl">
                  {p.image_url ? (
                    <img
                      src={p.image_url.startsWith('http') ? p.image_url : `${API}${p.image_url}`}
                      alt={p.title}
                      className="w-full h-auto object-cover transition-transform duration-500 group-hover:scale-105"
                      style={{ minHeight: '120px', maxHeight: '400px' }}
                      onError={(e) => { e.target.style.display = 'none'; }}
                    />
                  ) : (
                    <div className="w-full h-40 bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center">
                      <span className="text-3xl font-black text-white opacity-40">{p.title[0]}</span>
                    </div>
                  )}
                  <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-start justify-end p-3">
                    <button 
                      onClick={(e) => handleSave(e, p.id)}
                      className="bg-red-600 text-white px-4 py-2 rounded-full font-bold text-xs shadow-lg hover:bg-red-700 transition-colors"
                    >
                      Save
                    </button>
                  </div>
                </div>
                <div className="mt-2 px-1">
                  <p className="text-sm font-semibold text-gray-900 line-clamp-2">{p.title}</p>
                  {p.author && <p className="text-xs text-gray-400 mt-0.5 italic">By {p.author}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default PinDetail;