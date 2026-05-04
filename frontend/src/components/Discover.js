import React, { useEffect, useState } from 'react';
import './Discover.css';

const API = 'http://localhost:8000';

function Discover({ token }) {
  const [suggestions, setSuggestions] = useState([]);
  const [communities, setCommunities] = useState({});
  const [pprFeed, setPprFeed] = useState({ followed: [], discovery: [], serendipity: [] });
  const [loading, setLoading] = useState(true);

  const headers = { Authorization: `Bearer ${token}` };

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);

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
      setLoading(false);
    };

    fetchAll();
  }, [token]);

  if (loading) return <div className="discover-loading">Loading discoveries...</div>;

  // Grouper les communautés par id
  const communityGroups = {};
  for (const [username, commId] of Object.entries(communities)) {
    if (!communityGroups[commId]) communityGroups[commId] = [];
    communityGroups[commId].push(username);
  }

  return (
    <div className="discover-container">

      {/* Friend suggestions */}
      <div className="discover-card">
        <h2>👥 Friend Suggestions</h2>
        <p className="discover-subtitle">People you might want to follow (BFS)</p>
        {suggestions.length === 0 ? (
          <p className="discover-empty">No suggestions yet</p>
        ) : (
          <div className="suggestions-list">
            {suggestions.map((username, i) => (
              <div key={i} className="suggestion-item">
                <div className="suggestion-avatar">{username[0].toUpperCase()}</div>
                <span>{username}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Communities */}
      <div className="discover-card">
        <h2>🏘️ Communities (Louvain)</h2>
        <p className="discover-subtitle">Detected interest groups</p>
        {Object.entries(communityGroups).map(([commId, members]) => (
          <div key={commId} className="community-group">
            <p className="community-label">Community {commId}</p>
            <div className="community-members">
              {members.map((m, i) => (
                <span key={i} className="community-badge">{m}</span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* PPR Feed */}
      <div className="discover-card">
        <h2>⭐ Personalized Feed (PPR)</h2>
        <p className="discover-subtitle">Content ranked by PageRank score</p>

        {pprFeed.followed.length > 0 && (
          <div className="ppr-section">
            <p className="ppr-label">From people you follow</p>
            <div className="ppr-pins">
              {pprFeed.followed.map((pinId, i) => (
                <span key={i} className="ppr-pin">Pin #{pinId}</span>
              ))}
            </div>
          </div>
        )}

        {pprFeed.discovery.length > 0 && (
          <div className="ppr-section">
            <p className="ppr-label">Discovery</p>
            <div className="ppr-pins">
              {pprFeed.discovery.map((pinId, i) => (
                <span key={i} className="ppr-pin">Pin #{pinId}</span>
              ))}
            </div>
          </div>
        )}

        {pprFeed.serendipity.length > 0 && (
          <div className="ppr-section">
            <p className="ppr-label">Serendipity</p>
            <div className="ppr-pins">
              {pprFeed.serendipity.map((pinId, i) => (
                <span key={i} className="ppr-pin">Pin #{pinId}</span>
              ))}
            </div>
          </div>
        )}
      </div>

    </div>
  );
}

export default Discover;