import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';


const API = 'http://localhost:8000';

function Profile({ token, currentUserId }) {
  const { id } = useParams();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedBoard, setSelectedBoard] = useState(null);
  const [savedPins, setSavedPins] = useState([]);
  const [mySavedIds, setMySavedIds] = useState(new Set());
  const [showSaved, setShowSaved] = useState(false);
  const [savingId, setSavingId] = useState(null);
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

      // Fetch saved pins for THIS profile (the one being viewed)
      const savedRes = await fetch(`${API}/users/${id}/saved`, { headers });
      const savedData = await savedRes.json();
      setSavedPins(savedData.saved_pins || []);

      // If viewing someone else, also fetch MY saved pins to show correct button states
      if (String(id) !== String(currentUserId)) {
          const mySavedRes = await fetch(`${API}/users/${currentUserId}/saved`, { headers });
          const mySavedData = await mySavedRes.json();
          setMySavedIds(new Set(mySavedData.saved_pins.map(p => p.id)));
      } else {
          setMySavedIds(new Set(savedData.saved_pins.map(p => p.id)));
      }

    } catch (error) {
      console.error("Error fetching profile:", error);
    } finally {
      setLoading(false);
    }
  }, [id, token, currentUserId]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const handleSave = async (e, pinId) => {
    e.stopPropagation();
    const isAlreadySaved = mySavedIds.has(pinId);
    
    setSavingId(pinId);
    try {
      const method = isAlreadySaved ? 'DELETE' : 'POST';
      const res = await fetch(`${API}/pins/${pinId}/save`, {
        method: method,
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        setMySavedIds(prev => {
          const next = new Set(prev);
          if (isAlreadySaved) next.delete(pinId);
          else next.add(pinId);
          return next;
        });
        
        // If we are on our own profile and in the "Saved" tab, remove it from the visible list immediately
        if (showSaved && String(id) === String(currentUserId)) {
            setSavedPins(prev => prev.filter(p => p.id !== pinId));
        }
      }
    } catch (error) {
      console.error("Save error:", error);
    } finally {
      setSavingId(null);
    }
  };

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
        </div>
      </div>

      <div className="flex justify-center gap-8 mb-8 border-b border-gray-100 pb-2">
          <button 
            onClick={() => setShowSaved(false)}
            className={`pb-4 px-2 font-bold text-sm transition-all relative ${!showSaved ? 'text-black' : 'text-gray-400 hover:text-gray-600'}`}
          >
            Boards
            {!showSaved && <div className="absolute bottom-0 left-0 w-full h-1 bg-black rounded-full" />}
          </button>
          <button 
            onClick={() => setShowSaved(true)}
            className={`pb-4 px-2 font-bold text-sm transition-all relative ${showSaved ? 'text-black' : 'text-gray-400 hover:text-gray-600'}`}
          >
            Saved
            {showSaved && <div className="absolute bottom-0 left-0 w-full h-1 bg-black rounded-full" />}
          </button>
      </div>

      {!showSaved ? (
        <>
          {profile.boards.length === 0 ? (
            <div className="bg-gray-50 rounded-[32px] p-16 text-center border-2 border-dashed border-gray-200">
              <p className="text-gray-500 font-medium">You don't have any boards yet.</p>
              <button className="mt-4 text-red-600 font-bold hover:text-red-700 transition-colors">
                + Create my first board
              </button>
            </div>
          ) : (
            <>
              <div className="flex flex-wrap justify-center gap-3 mb-10 pb-6">
                {profile.boards.map(board => (
                  <button
                    key={board.id}
                    onClick={() => setSelectedBoard(board.id)}
                    className={`px-5 py-2.5 rounded-full font-bold text-sm transition-all duration-200 flex items-center gap-2 ${
                      selectedBoard === board.id
                        ? 'bg-gray-100 text-black shadow-sm'
                        : 'bg-white text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    {board.title}
                    <span className={`text-[10px] px-1.5 py-0.5 rounded-md ${
                      selectedBoard === board.id ? 'bg-white shadow-sm' : 'bg-gray-100'
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
                                          <PinCard 
                                            key={pin.id} 
                                            pin={pin} 
                                            navigate={navigate} 
                                            onSave={handleSave} 
                                            isSaved={mySavedIds.has(pin.id)}
                                            savingId={savingId}
                                          />
                                        ))
                                      )}
                                    </div>
                                  )}
                                </>
                              )}
                            </>
                          ) : (
                            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                              {savedPins.length === 0 ? (
                                <div className="col-span-full py-20 text-center bg-gray-50 rounded-[32px]">
                                  <p className="text-gray-400 font-medium italic">No saved pins yet.</p>
                                </div>
                              ) : (
                                savedPins.map(pin => (
                                  <PinCard 
                                    key={pin.id} 
                                    pin={pin} 
                                    navigate={navigate} 
                                    onSave={handleSave}
                                    isSaved={mySavedIds.has(pin.id)}
                                    savingId={savingId}
                                  />
                                ))
                              )}
                            </div>
                          )}
                        </div>
                      );
                    }
                    
                    function PinCard({ pin, navigate, onSave, isSaved, savingId }) {
                        return (
                            <div className="group cursor-pointer" onClick={() => navigate(`/pin/${pin.id}`)}>
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
                                    
                                                            onClick={(e) => onSave(e, pin.id)}
                                    
                                                            disabled={savingId === pin.id}
                                    
                                                            className={`${isSaved ? 'bg-black' : 'bg-red-600 hover:bg-red-700'} text-white px-4 py-2 rounded-full font-bold text-xs transform translate-y-2 group-hover:translate-y-0 transition-all duration-300 shadow-lg disabled:opacity-80`}
                                    
                                                        >
                                    
                                                            {savingId === pin.id ? '...' : isSaved ? 'Saved' : 'Save'}
                                    
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
                        );
                    }
                    

export default Profile;