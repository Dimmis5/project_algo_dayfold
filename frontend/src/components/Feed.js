import React, { useEffect, useState, useCallback } from 'react';
import './Feed.css';

const API = 'http://localhost:8000';

function Feed({ token }) {
  const [pins, setPins] = useState([]);
  const [loading, setLoading] = useState(true);
  const [antiScrollMessage, setAntiScrollMessage] = useState('');

  const headers = { Authorization: `Bearer ${token}` };

  const fetchFeed = useCallback(async () => {
    setLoading(true);
    const res = await fetch(`${API}/algo/feed`, { headers });
    const data = await res.json();
    setPins(data.feed || []);
    setAntiScrollMessage(data.message || '');
    setLoading(false);
  }, [token]);

  useEffect(() => {
    fetchFeed();
  }, [fetchFeed]);

  const handleLike = async (pinId) => {
    await fetch(`${API}/pins/${pinId}/like`, { method: 'POST', headers });
    setPins(prev => prev.map(p => p.id === pinId ? { ...p, likes: p.likes + 1 } : p));
  };

  if (loading) return <div className="feed-loading">Loading your feed...</div>;

  return (
    <div className="feed-container">
      {antiScrollMessage && (
        <div className="antiscroll-banner">
          {antiScrollMessage}
        </div>
      )}
      {pins.length === 0 ? (
        <div className="feed-empty">
          <h2>No pins yet</h2>
          <p>Create a board and add some pins to get started!</p>
        </div>
      ) : (
        <div className="feed-grid">
          {pins.map(pin => (
            <div key={pin.id} className="pin-card">
              <div className="pin-image-placeholder">
                <span>{pin.title[0]}</span>
              </div>
              <div className="pin-info">
                <p className="pin-title">{pin.title}</p>
                <button className="pin-like-btn" onClick={() => handleLike(pin.id)}>
                  ♥ {pin.likes}
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Feed;