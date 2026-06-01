import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';


const API = 'http://localhost:8000';

function Feed({ token }) {
  const [pins, setPins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [antiScrollMessage, setAntiScrollMessage] = useState('');
  const navigate = useNavigate();


  const fetchFeed = useCallback(async () => {
    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${token}` };
      const res = await fetch(`${API}/algo/feed`, { headers });
      const data = await res.json();
      
      setPins(data.feed || []);
      setAntiScrollMessage(data.message || '');
    } catch (error) {
      console.error("Erreur feed:", error);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchFeed();
  }, [fetchFeed]);

  const handleLike = async (pinId) => {
    const headers = { Authorization: `Bearer ${token}` };
    try {
      await fetch(`${API}/pins/${pinId}/like`, { method: 'POST', headers });
      setPins(prev => prev.map(p => 
        p.id === pinId ? { ...p, likes: p.likes + 1 } : p
      ));
    } catch (error) {
      console.error("Erreur like:", error);
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
      
      
{antiScrollMessage && antiScrollMessage !== "" && (
  <div className="mb-8 p-6 bg-gradient-to-r from-gray-900 to-gray-800 rounded-[24px] text-white shadow-xl relative overflow-hidden group">
          <div className="relative z-10">
            <h3 className="text-xl font-bold mb-1 flex items-center gap-2">
              <span className="text-red-500 text-2xl">✦</span> 
              Pause Créative
            </h3>
            <p className="text-gray-300 text-sm max-w-2xl italic">
              "{antiScrollMessage}"
            </p>
          </div>
          <div className="absolute top-[-20px] right-[-20px] w-32 h-32 bg-red-600/10 rounded-full blur-3xl group-hover:bg-red-600/20 transition-all"></div>
        </div>
      )}

      {pins.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 bg-gray-50 rounded-[40px] border-2 border-dashed border-gray-200">
          <div className="text-6xl mb-4">🎨</div>
          <h2 className="text-2xl font-bold text-gray-800">Votre flux est vide</h2>
          <p className="text-gray-500 mt-2 text-center max-w-md px-6">
            Explorez de nouveaux créateurs ou créez votre premier tableau pour commencer l'aventure Dayfold.
          </p>
        </div>
      ) : (
        /* GRILLE MASONRY */
        <div className="columns-2 md:columns-3 lg:columns-4 xl:columns-5 gap-4 space-y-4">
          {pins.map(pin => (
            <div 
              key={pin.id}
              onClick={() => navigate(`/pin/${pin.id}`)}  
              className="break-inside-avoid group cursor-zoom-in relative mb-4"
            >
              <div className="relative rounded-[20px] overflow-hidden bg-gray-100 shadow-sm transition-all duration-300 group-hover:shadow-xl border border-gray-100">
                
                {/* LOGIQUE D'AFFICHAGE IMAGE OU PLACEHOLDER */}
                {pin.image_url ? (
                  <img 
                    src={pin.image_url.startsWith('http') ? pin.image_url : `${API}${pin.image_url}`}
                    alt={pin.title}
                    className="w-full h-auto object-cover transition-transform duration-500 group-hover:scale-105"
                    style={{ minHeight: '150px', maxHeight: '500px' }}
                    onError={(e) => { e.target.style.display = 'none'; }} // Cache l'image si le lien est mort
                  />
                ) : (
                  /* PLACEHOLDER COLORÉ (si pas d'image) */
                  <div className={`w-full flex items-center justify-center text-white font-black text-5xl bg-gradient-to-br ${getRandomColor()}`} 
                       style={{ height: getRandomHeight() }}>
                    <span className="opacity-40 group-hover:scale-110 transition-transform duration-500">
                      {pin.title[0]}
                    </span>
                  </div>
                )}

                {/* OVERLAY AU SURVOL */}
                <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 p-3 flex flex-col justify-between">
                  <div className="flex justify-end">
                    <button 
                      className="bg-red-600 hover:bg-red-700 text-white px-5 py-2.5 rounded-full font-bold text-sm shadow-lg transform translate-y-[-10px] group-hover:translate-y-0 transition-all duration-300"
                    >
                      Enregistrer
                    </button>
                  </div>
                  
                  <div className="flex justify-between items-center">
                    <button className="bg-white/90 hover:bg-white p-2 rounded-full shadow-md text-gray-800 transition-colors">
                      🔗
                    </button>
                    <button className="bg-white/90 hover:bg-white p-2 rounded-full shadow-md text-gray-800 transition-colors">
                      ...
                    </button>
                  </div>
                </div>
              </div>

              {/* INFOS SOUS LE PIN */}
              <div className="mt-2 px-1 flex items-start justify-between">
                <div>
                  <p className="text-sm font-semibold text-gray-900 line-clamp-2 leading-tight">
                    {pin.title}
                  </p>
                  <p className="text-xs text-gray-500 mt-1 font-medium italic">Par Créateur #{pin.id}</p>
                </div>
                <button 
                  onClick={() => handleLike(pin.id)}
                  className="flex items-center gap-1 group/like active:scale-90 transition-transform"
                >
                  <span className="text-red-500 transition-transform group-hover/like:scale-125">♥</span>
                  <span className="text-xs font-bold text-gray-600">{pin.likes}</span>
                </button>
              </div>
            </div>
          ))}
        </div>
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