import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

const API = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function CommunityFeed({ token }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [pins, setPins] = useState([]);
  const [communityName, setCommunityName] = useState(`Community #${id}`);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCommunityFeed = async () => {
      setLoading(true);
      try {
        const headers = { Authorization: `Bearer ${token}` };
        const [pinsRes, communitiesRes] = await Promise.all([
          fetch(`${API}/algo/communities/${id}/pins`, { headers }),
          fetch(`${API}/algo/communities`, { headers })
        ]);

        const pinsData = await pinsRes.json();
        const communitiesData = await communitiesRes.json();

        setPins(pinsData.pins || []);
        setCommunityName(communitiesData.names?.[id] || `Community #${id}`);
      } catch (error) {
        console.error('Community feed error:', error);
        setPins([]);
      } finally {
        setLoading(false);
      }
    };

    fetchCommunityFeed();
  }, [id, token]);

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-[50vh]">
        <div className="flex gap-2">
          <div className="w-3 h-3 bg-emerald-600 rounded-full animate-bounce"></div>
          <div className="w-3 h-3 bg-emerald-600 rounded-full animate-bounce [animation-delay:-0.15s]"></div>
          <div className="w-3 h-3 bg-emerald-600 rounded-full animate-bounce [animation-delay:-0.3s]"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto px-2 md:px-8">
      <div className="flex items-center justify-between gap-4 mb-8">
        <div>
          <button
            onClick={() => navigate('/discover')}
            className="mb-3 text-sm font-bold text-gray-400 hover:text-black transition-colors"
          >
            Back to communities
          </button>
          <h1 className="text-3xl font-black tracking-tight text-gray-900">{communityName}</h1>
          <p className="text-sm text-gray-500 mt-1">
            {pins.length} posts published by members of this community
          </p>
        </div>
      </div>

      {pins.length === 0 ? (
        <div className="py-20 text-center bg-gray-50 rounded-[32px] border border-dashed border-gray-200">
          <p className="text-gray-400 font-medium italic">No posts in this community.</p>
        </div>
      ) : (
        <div className="columns-2 md:columns-3 lg:columns-4 xl:columns-5 gap-4 space-y-4">
          {pins.map(pin => (
            <div
              key={pin.id}
              onClick={() => navigate(`/pin/${pin.id}`)}
              className="break-inside-avoid group cursor-zoom-in relative mb-4"
            >
              <div className="relative rounded-[20px] overflow-hidden bg-gray-100 shadow-sm transition-all duration-300 group-hover:shadow-xl border border-gray-100">
                {pin.image_url ? (
                  <img
                    src={pin.image_url.startsWith('http') ? pin.image_url : `${API}${pin.image_url}`}
                    alt={pin.title}
                    className="w-full h-auto object-cover transition-transform duration-500 group-hover:scale-105"
                    style={{ minHeight: '150px', maxHeight: '500px' }}
                  />
                ) : (
                  <div className="w-full h-56 bg-gray-200 flex items-center justify-center text-5xl font-black text-white">
                    {pin.title[0]}
                  </div>
                )}
              </div>

              <div className="mt-2 px-1">
                <p className="text-sm font-semibold text-gray-900 line-clamp-2 leading-tight">{pin.title}</p>
                <p className="text-xs text-gray-500 mt-1 font-medium italic">
                  {pin.author ? `By ${pin.author}` : pin.category}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default CommunityFeed;
