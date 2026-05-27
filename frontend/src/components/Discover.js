import React, { useEffect, useState, useMemo } from 'react';

const API = 'http://localhost:8000';

function Discover({ token }) {
  const [suggestions, setSuggestions] = useState([]);
  const [communities, setCommunities] = useState({});
  const [pprFeed, setPprFeed] = useState({ followed: [], discovery: [], serendipity: [] });
  const [loading, setLoading] = useState(true);

  const handleSyncNeo4j = async () => {
  const res = await fetch(`${API}/algo/sync-graph`, {
    headers: { Authorization: `Bearer ${token}` }
  });
  if (res.ok) {
    alert("Graphe synchronisé ! Vous pouvez ouvrir Neo4j Browser.");
    window.open("http://localhost:7474", "_blank");
  }
};

  const handleFollow = async (userIdToFollow) => {
    try {
      const res = await fetch(`${API}/users/${userIdToFollow}/follow`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        setSuggestions(prev => prev.filter(u => u.id !== userIdToFollow));
      } else {
        const errorData = await res.json();
        console.error("Erreur follow:", errorData.detail);
      }
    } catch (error) {
      console.error("Erreur réseau lors du follow:", error);
    }
  };

  useEffect(() => {
    const fetchAll = async () => {
      try {
        setLoading(true);
        const headers = { Authorization: `Bearer ${token}` };
        
        const [resSugg, resComm, resPPR] = await Promise.all([
          fetch(`${API}/algo/suggest-friends`, { headers }),
          fetch(`${API}/algo/communities`, { headers }),
          fetch(`${API}/algo/ppr-feed`, { headers })
        ]);

        const suggData = await resSugg.json();
        const commData = await resComm.json();
        const pprData  = await resPPR.json();

        setSuggestions(suggData.suggestions || []);
        setCommunities(commData.communities || {});
        setPprFeed(pprData);
      } catch (e) {
        console.error("Erreur Discover:", e);
      } finally {
        setLoading(false);
      }
    };
    fetchAll();
  }, [token]);

  const communityGroups = useMemo(() => {
    const groups = {};
    if (!communities) return groups;
    for (const [username, commId] of Object.entries(communities)) {
      if (!groups[commId]) groups[commId] = [];
      groups[commId].push(username);
    }
    return groups;
  }, [communities]);

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
      <div className="w-12 h-12 border-4 border-gray-200 border-t-red-600 rounded-full animate-spin"></div>
      <p className="text-gray-500 font-medium animate-pulse">Calcul des graphes sociaux...</p>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-10">
      
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight italic">Exploration Dayfold</h1>
        <p className="text-gray-500 max-w-xl mx-auto">
          Découvrez les connexions invisibles de votre réseau grâce à nos algorithmes.
        </p>
      </div>
      <button 
        onClick={handleSyncNeo4j}
        className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-full font-bold shadow-lg transition-all active:scale-95"
      >
        Visualiser le Graphe (Neo4j) 📊
      </button>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <section className="bg-white p-8 rounded-[32px] border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <span className="text-blue-500">👥</span> Suggestions
            </h2>
            <span className="text-[10px] font-black bg-blue-50 text-blue-600 px-2 py-1 rounded uppercase tracking-tighter">BFS</span>
          </div>
          
          <p className="text-sm text-gray-500 mb-6 italic">Basé sur vos connexions communes.</p>
          
          <div className="space-y-4">
            {suggestions.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">Personne à suggérer pour le moment.</p>
            ) : (
              suggestions.map((user, i) => (
                <div key={user.id || i} className="flex items-center justify-between group">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center font-bold text-blue-600">
                      {user.username ? user.username[0].toUpperCase() : '?'}
                    </div>
                    <span className="font-semibold text-gray-700">{user.username}</span>
                  </div>
                  <button 
                    onClick={() => handleFollow(user.id)}
                    className="text-xs font-bold bg-black text-white px-4 py-2 rounded-full hover:bg-gray-800 transition-all active:scale-95"
                  >
                    Suivre
                  </button>
                </div>
              ))
            )}
          </div>
        </section>

        <section className="bg-white p-8 rounded-[32px] border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <span className="text-emerald-500">🏘️</span> Cercles
            </h2>
            <span className="text-[10px] font-black bg-emerald-50 text-emerald-600 px-2 py-1 rounded uppercase tracking-tighter">Louvain</span>
          </div>
          
          <p className="text-sm text-gray-500 mb-6 italic">Groupes d'intérêts organiques identifiés.</p>
          
          <div className="space-y-6">
            {Object.entries(communityGroups).length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">Recherche de communautés...</p>
            ) : (
              Object.entries(communityGroups).map(([commId, members]) => (
                <div key={commId} className="p-4 bg-gray-50 rounded-2xl border border-gray-100">
                  <p className="text-[10px] font-bold text-emerald-600 uppercase mb-3 tracking-widest">Cercle #{commId}</p>
                  <div className="flex flex-wrap gap-2">
                    {members.map((m, i) => (
                      <span key={i} className="px-2.5 py-1 bg-white border border-gray-200 text-gray-700 text-xs font-medium rounded-lg shadow-sm">
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

        <section className="bg-white p-8 rounded-[32px] border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <span className="text-purple-500">⭐</span> Ranking
            </h2>
            <span className="text-[10px] font-black bg-purple-50 text-purple-600 px-2 py-1 rounded uppercase tracking-tighter">PPR</span>
          </div>

          <p className="text-sm text-gray-500 mb-6 italic">Contenu priorisé par score d'influence.</p>

          <div className="space-y-4">
            {[
              { label: 'Abonnements', data: pprFeed?.followed, color: 'bg-red-500' },
              { label: 'Découverte', data: pprFeed?.discovery, color: 'bg-blue-500' },
              { label: 'Sérendipité', data: pprFeed?.serendipity, color: 'bg-amber-500' }
            ].map((section, idx) => (section.data && section.data.length > 0) && (
              <div key={idx} className="space-y-2">
                <p className="text-[11px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                  <span className={`w-1.5 h-1.5 rounded-full ${section.color}`}></span>
                  {section.label}
                </p>
                <div className="flex flex-wrap gap-2">
                  {section.data.map((pinId, i) => (
                    <div key={i} className="px-3 py-2 bg-gray-50 border border-gray-200 rounded-xl text-xs font-bold text-gray-600">
                      Pin #{pinId}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

      </div>
    </div>
  );
}

export default Discover;