import React, { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';

const API = 'http://localhost:8000';

function Discover({ token }) {
  const [suggestions, setSuggestions] = useState([]);
  const [communities, setCommunities] = useState({});
  const [pprFeed, setPprFeed] = useState({ followed: [], discovery: [], serendipity: [] });
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const handleSyncNeo4j = async () => {
    const res = await fetch(`${API}/algo/sync-graph`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    if (res.ok) {
      alert("Graph synchronized! You can open Neo4j Browser.");
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
        console.error("Follow error:", errorData.detail);
      }
    } catch (error) {
      console.error("Network error during follow:", error);
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
        console.error("Discover error:", e);
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

  const PinCard = ({ pin }) => (
    <div 
      onClick={() => navigate(`/pin/${pin.id}`)}
      className="flex flex-col gap-2 group cursor-pointer min-w-[140px] max-w-[140px]"
    >
      <div className="relative aspect-[4/5] bg-gray-100 rounded-xl overflow-hidden border border-gray-100 shadow-sm group-hover:shadow-md transition-all">
        {pin.image_url ? (
          <img 
            src={pin.image_url.startsWith('http') ? pin.image_url : `${API}/uploads/${pin.image_url}`} 
            alt={pin.title}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-2xl font-black text-gray-300">
            {pin.title[0]}
          </div>
        )}
      </div>
      <div className="px-1">
        <p className="text-[11px] font-bold text-gray-800 truncate leading-tight">{pin.title}</p>
        <p className="text-[10px] text-gray-500 font-medium">@{pin.author}</p>
      </div>
    </div>
  );

  if (loading) return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
      <div className="w-12 h-12 border-4 border-gray-200 border-t-red-600 rounded-full animate-spin"></div>
      <p className="text-gray-500 font-medium animate-pulse">Calculating social graphs...</p>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-12">
      
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div className="space-y-2">
          <h1 className="text-4xl font-black text-gray-900 tracking-tight italic">Algorithmic Tracking</h1>
          <p className="text-gray-500 max-w-xl">
            Discover how Dayfold analyzes your relationships and interests to shape your experience.          </p>
        </div>
        <button 
          onClick={handleSyncNeo4j}
          className="bg-indigo-600 hover:bg-indigo-700 text-white px-8 py-3 rounded-full font-bold shadow-lg transition-all active:scale-95 flex items-center gap-2"
        >
          <span>📊</span>
          Live Graph Analysis (Neo4j)
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        <section className="bg-white p-8 rounded-[40px] border border-gray-100 shadow-sm hover:shadow-md transition-shadow flex flex-col">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <span className="text-blue-500">👥</span> Friend Suggestions
            </h2>
            <span className="text-[10px] font-black bg-blue-50 text-blue-600 px-2.5 py-1 rounded-lg uppercase tracking-wider">BFS Algorithm</span>
          </div>
          <p className="text-xs text-gray-400 mb-8 leading-relaxed">
            Breadth-first search of the social graph to identify "friends of friends" with the shortest distance.
          </p>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {suggestions.length === 0 ? (
              <p className="col-span-full text-sm text-gray-400 text-center py-10 bg-gray-50 rounded-3xl border border-dashed border-gray-200 italic">
Your entire local network has already been explored.              </p>
            ) : (
              suggestions.map((user, i) => (
                <div key={user.id || i} className="flex items-center justify-between p-3 bg-gray-50 rounded-2xl border border-transparent hover:border-blue-100 transition-colors">
                  <div className="flex items-center gap-3">
                    <div 
                      onClick={() => navigate(`/profile/${user.id}`)}
                      className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center font-bold text-blue-600 cursor-pointer hover:scale-105 transition-transform"
                    >
                      {user.username ? user.username[0].toUpperCase() : '?'}
                    </div>
                    <span 
                      onClick={() => navigate(`/profile/${user.id}`)}
                      className="font-bold text-gray-700 text-sm cursor-pointer hover:underline"
                    >
                      {user.username}
                    </span>
                  </div>
                  <button 
                    onClick={() => handleFollow(user.id)}
                    className="text-[10px] font-black bg-black text-white px-4 py-2 rounded-full hover:bg-gray-800 transition-all active:scale-95"
                  >
                    FOLLOW
                  </button>
                </div>
              ))
            )}
          </div>
        </section>

        <section className="bg-white p-8 rounded-[40px] border border-gray-100 shadow-sm hover:shadow-md transition-shadow flex flex-col">
          <div className="flex items-center justify-between mb-2">
            <h2 className="text-xl font-bold flex items-center gap-2">
              <span className="text-emerald-500">🏘️</span> Community Circles
            </h2>
            <span className="text-[10px] font-black bg-emerald-50 text-emerald-600 px-2.5 py-1 rounded-lg uppercase tracking-wider">Louvain Method</span>
          </div>
          <p className="text-xs text-gray-400 mb-8 leading-relaxed">
Modular detection of clusters of interest. Groups users with dense interactions.          </p>
          
          <div className="flex flex-wrap gap-4">
            {Object.entries(communityGroups).length === 0 ? (
              <p className="w-full text-sm text-gray-400 text-center py-10 bg-gray-50 rounded-3xl border border-dashed border-gray-200 italic">
Community calculations are in progress...              </p>
            ) : (
              Object.entries(communityGroups).map(([commId, members]) => (
                <div key={commId} className="flex-1 min-w-[200px] p-5 bg-gray-50 rounded-3xl border border-emerald-50 relative overflow-hidden group">
                  <div className="absolute top-0 right-0 p-3 opacity-10 group-hover:scale-110 transition-transform">
                    <span className="text-4xl font-black text-emerald-600">#{commId}</span>
                  </div>
                  <p className="text-[10px] font-black text-emerald-600 uppercase mb-4 tracking-[0.2em] relative z-10">Circle Alpha</p>
                  <div className="flex flex-wrap gap-2 relative z-10">
                    {members.map((m, i) => (
                      <span key={i} className="px-3 py-1.5 bg-white border border-gray-100 text-gray-700 text-[10px] font-bold rounded-xl shadow-sm">
                        {m}
                      </span>
                    ))}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
      </div>

      <section className="bg-white p-10 rounded-[48px] border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10">
          <div className="space-y-1">
            <h2 className="text-2xl font-black flex items-center gap-2 italic">
              <span className="text-purple-500">⭐</span> Personalized Ranking
            </h2>
            <p className="text-sm text-gray-400 max-w-2xl">
              Analyse by <strong>Personalized PageRank (PPR)</strong>. The closer a piece of content is to your interests and subscriptions in the graph, the higher its score.

</p>
          </div>
          <span className="self-start md:self-center text-[10px] font-black bg-purple-50 text-purple-600 px-4 py-2 rounded-xl uppercase tracking-[0.2em]">PPR Engine V2</span>
        </div>

        <div className="space-y-12">
          {[
            { 
              label: 'Direct Network', 
              desc: 'Content from the people you follow..',
              data: pprFeed?.followed, 
              color: 'bg-red-500', 
              empty: 'No recent content on your network.' 
            },
            { 
              label: 'Discovery', 
              desc: 'Recommended content based on your shared interests.',
              data: pprFeed?.discovery, 
              color: 'bg-blue-500', 
              empty: 'Explore more content to refine your recommendations.' 
            },
            { 
              label: 'Random', 
              desc: 'The positive "noise": distant content to break your filter bubble.',
              data: pprFeed?.serendipity, 
              color: 'bg-amber-500', 
              empty: 'The serendipity engine is recalibrating itself.' 
            }
          ].map((section, idx) => (
            <div key={idx} className="space-y-6">
              <div className="flex items-end gap-3 px-2">
                <div className={`w-1.5 h-8 rounded-full ${section.color}`}></div>
                <div>
                  <h3 className="text-sm font-black uppercase tracking-widest text-gray-900 leading-none">{section.label}</h3>
                  <p className="text-[11px] text-gray-400 font-medium mt-1 italic">{section.desc}</p>
                </div>
              </div>
              
              <div className="flex gap-6 overflow-x-auto pb-4 px-2 scrollbar-hide">
                {!section.data || section.data.length === 0 ? (
                  <p className="text-xs text-gray-300 italic py-6">{section.empty}</p>
                ) : (
                  section.data.map((pin, i) => (
                    <PinCard key={pin.id || i} pin={pin} />
                  ))
                )}
              </div>
            </div>
          ))}
        </div>
      </section>

    </div>
  );
}

export default Discover;