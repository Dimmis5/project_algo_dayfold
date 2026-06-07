import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';


const API = 'http://localhost:8000';

function Profile({ token, currentUserId }) {
  const { id } = useParams();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedBoard, setSelectedBoard] = useState(null);
  const navigate = useNavigate();


  const fetchProfile = useCallback(async () => {
    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${token}` };
      const res = await fetch(`${API}/users/${id}/profile`, { headers });
      const data = await res.json();
      
      setProfile(data);
      if (data.boards && data.boards.length > 0) {
        setSelectedBoard(data.boards[0].id);
      }
    } catch (error) {
      console.error("Error fetching profile:", error);
    } finally {
      setLoading(false);
    }
  }, [id, token]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const handleFollow = async () => {
    try {
      const res = await fetch(`${API}/users/${id}/follow`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        setProfile(prev => ({
          ...prev,
          is_following: true,
          followers: prev.followers + 1
        }));
      } else {
        const errorData = await res.json();
        console.error("Follow error:", errorData.detail);
      }
    } catch (error) {
      console.error("Network error during follow:", error);
    }
  };

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      <p className="mt-4 text-gray-500 font-medium italic">Loading Dayfold profile...</p>
    </div>
  );

  if (!profile) return (
    <div className="text-center py-20 text-gray-500">User not found.</div>
  );

  const currentBoard = profile.boards.find(b => b.id === selectedBoard);
  const isOwnProfile = String(currentUserId) === String(id);

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      
      <div className="flex flex-col items-center text-center mb-12">
        <div className="w-32 h-32 rounded-full bg-gray-100 border border-gray-200 flex items-center justify-center text-4xl font-bold text-gray-700 shadow-sm mb-4">
          {profile.user.username[0].toUpperCase()}
        </div>
        
        <div className="flex items-center gap-2 mb-2">
          <h1 className="text-3xl font-bold text-gray-900">{profile.user.username}</h1>
          {profile.user.is_admin && (
            <span className="px-2 py-0.5 bg-gray-800 text-white text-[10px] font-black rounded uppercase tracking-widest">
              Admin
            </span>
          )}
        </div>

        <div className="flex items-center gap-6 text-sm font-medium text-gray-600 mt-2">
          <button className="hover:underline">
            <span className="text-gray-900 font-bold">{profile.followers}</span> followers
          </button>
          <button className="hover:underline">
            <span className="text-gray-900 font-bold">{profile.following}</span> following
          </button>
        </div>

        <div className="mt-6 flex gap-3">
          {isOwnProfile ? (
            <button className="px-6 py-2.5 bg-gray-100 text-gray-900 font-bold rounded-full hover:bg-gray-200 transition-colors">
              Edit Profile
            </button>
          ) : (
            <button 
              onClick={handleFollow}
              disabled={profile.is_following}
              className={`px-8 py-2.5 rounded-full font-bold transition-all active:scale-95 ${
                profile.is_following 
                  ? 'bg-gray-100 text-gray-500 cursor-default' 
                  : 'bg-red-600 text-white hover:bg-red-700 shadow-md'
              }`}
            >
              {profile.is_following ? 'Following' : 'Follow'}
            </button>
          )}
          <button className="p-2.5 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
              <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
            </svg>
          </button>
        </div>
      </div>

      {profile.boards.length === 0 ? (
        <div className="bg-gray-50 rounded-[32px] p-16 text-center border-2 border-dashed border-gray-200">
          <p className="text-gray-500 font-medium">You don't have any boards yet.</p>
          <button className="mt-4 text-red-600 font-bold hover:text-red-700 transition-colors">
            + Create my first board
          </button>
        </div>
      ) : (
        <>
          <div className="flex flex-wrap justify-center gap-3 mb-10 border-b border-gray-100 pb-6">
            {profile.boards.map(board => (
              <button
                key={board.id}
                onClick={() => setSelectedBoard(board.id)}
                className={`px-5 py-2.5 rounded-full font-bold text-sm transition-all duration-200 flex items-center gap-2 ${
                  selectedBoard === board.id
                    ? 'bg-black text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                {board.title}
                <span className={`text-[10px] px-1.5 py-0.5 rounded-md ${
                  selectedBoard === board.id ? 'bg-gray-800' : 'bg-gray-200'
                }`}>
                  {board.pins.length}
                </span>
              </button>
            ))}
          </div>

          {currentBoard && (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
              {currentBoard.pins.length === 0 ? (
                <div className="col-span-full py-20 text-center bg-gray-50 rounded-[32px]">
                  <p className="text-gray-400 font-medium italic">This board is still empty.</p>
                </div>
              ) : (
                currentBoard.pins.map(pin => (
                  <div key={pin.id} className="group cursor-pointer" onClick={() => navigate(`/pin/${pin.id}`)}>
                    <div className="relative aspect-[3/4] w-full rounded-2xl bg-gray-100 flex items-center justify-center overflow-hidden shadow-sm transition-all duration-300 group-hover:shadow-xl">
                      {pin.image_url ? (
                        <img 
                          src={pin.image_url.startsWith('http') ? pin.image_url : `${API}${pin.image_url}`} 
                          alt={pin.title}
                          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                        />
                      ) : (
                        <span className="text-4xl font-black text-gray-300 opacity-40 group-hover:scale-110 transition-transform">
                          {pin.title[0]}
                        </span>
                      )}
                      
                      <div className="absolute inset-0 bg-black/5 opacity-0 group-hover:opacity-100 transition-opacity flex items-start justify-end p-3">
                        <button 
                          onClick={(e) => {
                            e.stopPropagation();
                            // logic for save could be added here
                          }}
                          className="bg-red-600 text-white px-4 py-2 rounded-full font-bold text-xs transform translate-y-2 group-hover:translate-y-0 transition-all duration-300 shadow-lg"
                        >
                          Save
                        </button>
                      </div>
                    </div>
                    
                    <div className="mt-2 px-1">
                      <p className="text-sm font-bold text-gray-800 truncate leading-tight">
                        {pin.title}
                      </p>
                      <div className="flex items-center gap-1 mt-1">
                        <span className="text-red-500 text-xs font-bold">♥</span>
                        <span className="text-[11px] text-gray-500 font-semibold">{pin.likes}</span>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default Profile;