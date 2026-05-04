import React, { useEffect, useState, useCallback } from 'react';
import './Profile.css';

const API = 'http://localhost:8000';

function Profile({ token, userId }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedBoard, setSelectedBoard] = useState(null);

  const headers = { Authorization: `Bearer ${token}` };

  const fetchProfile = useCallback(async () => {
    setLoading(true);
    const res = await fetch(`${API}/users/${userId}/profile`, { headers });
    const data = await res.json();
    setProfile(data);
    if (data.boards && data.boards.length > 0) {
      setSelectedBoard(data.boards[0].id);
    }
    setLoading(false);
  }, [userId, token]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  if (loading) return <div className="profile-loading">Loading profile...</div>;
  if (!profile) return null;

  const currentBoard = profile.boards.find(b => b.id === selectedBoard);

  return (
    <div className="profile-container">

      {/* Header */}
      <div className="profile-header">
        <div className="profile-avatar">
          {profile.user.username[0].toUpperCase()}
        </div>
        <h1 className="profile-username">{profile.user.username}</h1>
        {profile.user.is_admin && <span className="profile-admin-badge">Admin</span>}
        <div className="profile-stats">
          <div className="profile-stat">
            <span className="stat-number">{profile.followers}</span>
            <span className="stat-label">Followers</span>
          </div>
          <div className="profile-stat">
            <span className="stat-number">{profile.following}</span>
            <span className="stat-label">Following</span>
          </div>
          <div className="profile-stat">
            <span className="stat-number">{profile.boards.length}</span>
            <span className="stat-label">Boards</span>
          </div>
        </div>
      </div>

      {/* Boards tabs */}
      {profile.boards.length === 0 ? (
        <div className="profile-empty">
          <p>No boards yet. Create one!</p>
        </div>
      ) : (
        <>
          <div className="boards-tabs">
            {profile.boards.map(board => (
              <button
                key={board.id}
                className={`board-tab ${selectedBoard === board.id ? 'board-tab-active' : ''}`}
                onClick={() => setSelectedBoard(board.id)}
              >
                {board.title}
                <span className="board-tab-count">{board.pins.length}</span>
              </button>
            ))}
          </div>

          {currentBoard && (
            <div className="profile-pins-grid">
              {currentBoard.pins.length === 0 ? (
                <p className="profile-empty">No pins in this board yet.</p>
              ) : (
                currentBoard.pins.map(pin => (
                  <div key={pin.id} className="profile-pin-card">
                    <div className="profile-pin-image">
                      <span>{pin.title[0]}</span>
                    </div>
                    <div className="profile-pin-info">
                      <p className="profile-pin-title">{pin.title}</p>
                      <p className="profile-pin-likes">♥ {pin.likes}</p>
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