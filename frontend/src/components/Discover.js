import React, { useEffect, useState, useMemo } from 'react';

const API = 'http://localhost:8000';

function Discover({ token }) {
  const [suggestions, setSuggestions] = useState([]);
  const [communities, setCommunities] = useState({});
  const [pprFeed, setPprFeed] = useState({ followed: [], discovery: [], serendipity: [] });
  const [loading, setLoading] = useState(true);

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

  // Regroupement des communautés optimisé
  const communityGroups = useMemo(() => {
    const groups = {};
    for (const [username, commId] of Object.entries(communities)) {
      if (!groups[commId]) groups[commId] = [];
      groups[commId].push(username);
    }
    return groups;
  }, [communities]);

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
      <div className="w-12 h-12 border-4 border-gray-200 border-t-red-600 rounded-full animate-spin"></div>
      <p className="text-gray-500 font-medium animate-pulse">Analyse des graphes en cours...</p>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-10">
      
      {/* HEADER DE LA PAGE */}
      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">Exploration Algorithmique</h1>
        <p className="text-gray-500 max-w-xl mx-auto">
          Découvrez comment l'intelligence de Dayfold connecte les créateurs et organise le contenu.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* 1. SUGGESTIONS D'AMIS (BFS) */}
        <section className="bg-white p-8 rounded-[32px] border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <span className="text-blue-500">👥</span> Suggestions
            </h2>
            <span className="text-[10px] font-black bg-blue-50 text-blue-600 px-2 py-1 rounded uppercase tracking-tighter">BFS Algo</span>
          </div>
          
          <p className="text-sm text-gray-500 mb-6 italic">Personnes que vous pourriez connaître via votre réseau.</p>
          
          <div className="space-y-4">
            {suggestions.length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">Aucune suggestion pour le moment.</p>
            ) : (
              suggestions.map((username, i) => (
                <div key={i} className="flex items-center justify-between group">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-blue-100 to-blue-50 flex items-center justify-center font-bold text-blue-600 border border-blue-200">
                      {username[0].toUpperCase()}
                    </div>
                    <span className="font-semibold text-gray-700 group-hover:text-black transition-colors">{username}</span>
                  </div>
                  <button className="text-xs font-bold bg-gray-100 hover:bg-black hover:text-white px-3 py-1.5 rounded-full transition-all">Suivre</button>
                </div>
              ))
            )}
          </div>
        </section>

        {/* 2. COMMUNAUTÉS (LOUVAIN) */}
        <section className="bg-white p-8 rounded-[32px] border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <span className="text-emerald-500">🏘️</span> Cercles
            </h2>
            <span className="text-[10px] font-black bg-emerald-50 text-emerald-600 px-2 py-1 rounded uppercase tracking-tighter">Louvain</span>
          </div>
          
          <p className="text-sm text-gray-500 mb-6 italic">Groupes d'intérêts organiques détectés dans le réseau.</p>
          
          <div className="space-y-6">
            {Object.entries(communityGroups).length === 0 ? (
              <p className="text-sm text-gray-400 text-center py-4">Analyse des cercles en cours...</p>
            ) : (
              Object.entries(communityGroups).map(([commId, members]) => (
                <div key={commId} className="p-4 bg-emerald-50/30 rounded-2xl border border-emerald-100">
                  <p className="text-[10px] font-bold text-emerald-600 uppercase mb-3 tracking-widest">Cercle Créatif #{commId}</p>
                  <div className="flex flex-wrap gap-2">
                    {members.map((m, i) => (
                      <span key={i} className="px-2.5 py-1 bg-white border border-emerald-200 text-emerald-700 text-xs font-medium rounded-lg shadow-sm">
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

        {/* 3. FLUX PERSONNALISÉ (PAGE RANK) */}
        <section className="bg-white p-8 rounded-[32px] border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <span className="text-purple-500">⭐</span> Ranking
            </h2>
            <span className="text-[10px] font-black bg-purple-50 text-purple-600 px-2 py-1 rounded uppercase tracking-tighter">PPR Score</span>
          </div>

          <p className="text-sm text-gray-500 mb-6 italic">Contenu classé selon votre influence et vos interactions.</p>

          <div className="space-y-4">
            {[
              { label: 'Abonnements', data: pprFeed.followed, color: 'bg-red-500' },
              { label: 'Découverte', data: pprFeed.discovery, color: 'bg-blue-500' },
              { label: 'Sérendipité', data: pprFeed.serendipity, color: 'bg-amber-500' }
            ].map((section, idx) => section.data.length > 0 && (
              <div key={idx} className="space-y-2">
                <p className="text-[11px] font-bold text-gray-400 uppercase tracking-widest flex items-center gap-2">
                  <span className={`w-1.5 h-1.5 rounded-full ${section.color}`}></span>
                  {section.label}
                </p>
                <div className="flex flex-wrap gap-2">
                  {section.data.map((pinId, i) => (
                    <div key={i} className="px-3 py-2 bg-gray-50 hover:bg-gray-100 border border-gray-200 rounded-xl text-xs font-bold text-gray-600 transition-colors cursor-pointer">
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