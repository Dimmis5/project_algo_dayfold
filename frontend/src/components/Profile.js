import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';


const API = 'http://localhost:8000';

function Profile({ token, userId }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedBoard, setSelectedBoard] = useState(null);
  const navigate = useNavigate();


  const fetchProfile = useCallback(async () => {
    try {
      setLoading(true);
      const headers = { Authorization: `Bearer ${token}` };
      const res = await fetch(`${API}/users/${userId}/profile`, { headers });
      const data = await res.json();
      
      setProfile(data);
      if (data.boards && data.boards.length > 0) {
        setSelectedBoard(data.boards[0].id);
      }
    } catch (error) {
      console.error("Erreur lors de la récupération du profil:", error);
    } finally {
      setLoading(false);
    }
  }, [userId, token]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh]">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      <p className="mt-4 text-gray-500 font-medium italic">Chargement du profil Dayfold...</p>
    </div>
  );

  if (!profile) return (
    <div className="text-center py-20 text-gray-500">Utilisateur introuvable.</div>
  );

  const currentBoard = profile.boards.find(b => b.id === selectedBoard);

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
            <span className="text-gray-900 font-bold">{profile.followers}</span> abonnés
          </button>
          <button className="hover:underline">
            <span className="text-gray-900 font-bold">{profile.following}</span> abonnements
          </button>
        </div>
      </div>

      {profile.boards.length === 0 ? (
        <div className="bg-gray-50 rounded-[32px] p-16 text-center border-2 border-dashed border-gray-200">
          <p className="text-gray-500 font-medium">Vous n'avez pas encore de tableaux.</p>
          <button className="mt-4 text-red-600 font-bold hover:text-red-700 transition-colors">
            + Créer mon premier tableau
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
                  <p className="text-gray-400 font-medium italic">Ce tableau est encore vide.</p>
                </div>
              ) : (
                currentBoard.pins.map(pin => (
                  <div key={pin.id} className="group cursor-pointer">
                    onClick={() => navigate(`/pin/${pin.id}`)}
                    <div className="relative aspect-[3/4] w-full rounded-2xl bg-gradient-to-br from-gray-50 to-gray-200 flex items-center justify-center overflow-hidden shadow-sm transition-all duration-300 group-hover:shadow-xl">
                      <span className="text-4xl font-black text-white opacity-40 group-hover:scale-110 transition-transform">
                        {pin.title[0]}
                      </span>
                      
                      <div className="absolute inset-0 bg-black/5 opacity-0 group-hover:opacity-100 transition-opacity flex items-start justify-end p-3">
                        <button className="bg-red-600 text-white px-4 py-2 rounded-full font-bold text-xs transform translate-y-2 group-hover:translate-y-0 transition-all duration-300 shadow-lg">
                          Enregistrer
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