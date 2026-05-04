import React, { useEffect, useState, useCallback } from 'react';
import './Feed.css';

const API = 'http://localhost:8000';

function Feed({ token }) {
  const [pins, setPins] = useState([]);
  const [loading, setLoading] = useState(true);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchBoards = useCallback(async () => {
    setLoading(true);
    const res = await fetch(`${API}/boards`, { headers });
    const boards = await res.json();

    const allPins = [];
    for (const board of boards) {
      const res2 = await fetch(`${API}/pins/${board.id}`, { headers });
      const pins = await res2.json();
      allPins.push(...pins.map(p => ({ ...p, boardTitle: board.title, category: board.category })));
    }
    setPins(allPins);
    setLoading(false);
  }, [token]);

  useEffect(() => {
    fetchBoards();
  }, [fetchBoards]);

  const handleLike = async (pinId) => {
    await fetch(`${API}/pins/${pinId}/like`, { method: 'POST', headers });
    setPins(prev => prev.map(p => p.id === pinId ? { ...p, likes: p.likes + 1 } : p));
  };

  if (loading) return <div className="feed-loading">Loading your feed...</div>;

  return (
    <div className="feed-container">
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
                <p className="pin-board">{pin.boardTitle} · {pin.category}</p>
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