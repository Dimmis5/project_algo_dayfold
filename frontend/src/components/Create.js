import React, { useEffect, useState, useCallback } from 'react';
import './Create.css';

const API = 'http://localhost:8000';

function Create({ token }) {
  const [boards, setBoards] = useState([]);
  const [boardForm, setBoardForm] = useState({ title: '', category: '' });
  const [pinForm, setPinForm] = useState({ title: '', board_id: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const headers = {
    Authorization: `Bearer ${token}`,
    'Content-Type': 'application/json'
  };

  const fetchBoards = useCallback(async () => {
    const res = await fetch(`${API}/boards`, { headers });
    const data = await res.json();
    setBoards(data);
  }, [token]);

  useEffect(() => {
    fetchBoards();
  }, [fetchBoards]);

  const handleCreateBoard = async () => {
    setError('');
    setSuccess('');
    if (!boardForm.title || !boardForm.category) {
      setError('Please fill in all fields');
      return;
    }
    const res = await fetch(`${API}/boards`, {
      method: 'POST',
      headers,
      body: JSON.stringify(boardForm)
    });
    if (res.ok) {
      setBoardForm({ title: '', category: '' });
      setSuccess('Board created successfully!');
      fetchBoards();
    } else {
      setError('Error creating board');
    }
  };

  const handleCreatePin = async () => {
    setError('');
    setSuccess('');
    if (!pinForm.title || !pinForm.board_id) {
      setError('Please fill in all fields');
      return;
    }
    const res = await fetch(`${API}/pins`, {
      method: 'POST',
      headers,
      body: JSON.stringify({ ...pinForm, board_id: parseInt(pinForm.board_id) })
    });
    if (res.ok) {
      setPinForm({ title: '', board_id: '' });
      setSuccess('Pin created successfully!');
    } else {
      setError('Error creating pin');
    }
  };

  return (
    <div className="create-container">

      {error && <p className="create-error">{error}</p>}
      {success && <p className="create-success">{success}</p>}

      {/* Board form */}
      <div className="create-card">
        <h2>Create a Board</h2>
        <input
          className="create-input"
          placeholder="Board title"
          value={boardForm.title}
          onChange={e => setBoardForm({ ...boardForm, title: e.target.value })}
        />
        <input
          className="create-input"
          placeholder="Category (e.g. Décoration, Tech, Art)"
          value={boardForm.category}
          onChange={e => setBoardForm({ ...boardForm, category: e.target.value })}
        />
        <button className="create-btn" onClick={handleCreateBoard}>Create Board</button>
      </div>

      {/* Pin form */}
      <div className="create-card">
        <h2>Create a Pin</h2>
        <input
          className="create-input"
          placeholder="Pin title"
          value={pinForm.title}
          onChange={e => setPinForm({ ...pinForm, title: e.target.value })}
        />
        <select
          className="create-input"
          value={pinForm.board_id}
          onChange={e => setPinForm({ ...pinForm, board_id: e.target.value })}
        >
          <option value="">Select a board</option>
          {boards.map(b => (
            <option key={b.id} value={b.id}>{b.title}</option>
          ))}
        </select>
        <button className="create-btn" onClick={handleCreatePin}>Create Pin</button>
      </div>

    </div>
  );
}

export default Create;