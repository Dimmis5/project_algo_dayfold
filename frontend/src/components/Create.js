import React, { useEffect, useState, useCallback } from 'react';

const API = 'http://localhost:8000';

function Create({ token }) {
  const [boards, setBoards] = useState([]);
  const [boardForm, setBoardForm] = useState({ title: '', category: '' });
  const [pinForm, setPinForm] = useState({ title: '', board_id: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [file, setFile] = useState(null);


  const fetchBoards = useCallback(async () => {
    try {
      const headers = { Authorization: `Bearer ${token}` };
      const res = await fetch(`${API}/boards`, { headers });
      const data = await res.json();
      setBoards(data);
    } catch (e) {
      console.error("Error loading boards:", e);
    }
  }, [token]);

  useEffect(() => {
    fetchBoards();
  }, [fetchBoards]);

  const showMessage = (msg, isError = false) => {
    if (isError) setError(msg);
    else setSuccess(msg);
    setTimeout(() => {
      setError('');
      setSuccess('');
    }, 4000);
  };

  const handleCreateBoard = async () => {
    if (!boardForm.title || !boardForm.category) {
      showMessage('Please fill in all the fields in the table', true);
      return;
    }
    const headers = {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    };
    const res = await fetch(`${API}/boards`, {
      method: 'POST',
      headers,
      body: JSON.stringify(boardForm)
    });
    if (res.ok) {
      setBoardForm({ title: '', category: '' });
      showMessage('Board created successfully!');
      fetchBoards();
    } else {
      showMessage('Error creating board', true);
    }
  };

const handleCreatePin = async () => {
  if (!pinForm.title || !pinForm.board_id || !file) {
    showMessage("Title, board, or image is missing!", true);
    return;
  }

  const formData = new FormData();
  formData.append('title', pinForm.title);
  formData.append('board_id', pinForm.board_id);
  formData.append('file', file);

  const res = await fetch(`${API}/pins`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}` }, 
    body: formData
  });

  if (res.ok) {
    setPinForm({ title: '', board_id: '' });
    setFile(null);
    showMessage('Pin published!');
  }
};

  const inputStyle = "w-full px-4 py-3 bg-gray-50 border-2 border-transparent rounded-2xl focus:bg-white focus:border-red-400 focus:ring-0 outline-none transition-all placeholder:text-gray-400 text-gray-700";

  return (
    <div className="max-w-4xl mx-auto px-4 py-12">
      
      <div className="mb-12 text-center">
        <h1 className="text-3xl font-extrabold text-gray-900">New Creation</h1>
        <p className="text-gray-500 mt-2">Bring your ideas to life and organize your inspirations.</p>
      </div>

      <div className="fixed bottom-10 left-1/2 -translate-x-1/2 z-50 space-y-2 w-full max-w-xs md:max-w-sm">
        {error && (
          <div className="bg-red-600 text-white px-6 py-4 rounded-2xl shadow-2xl animate-bounce flex items-center gap-3">
            <span>⚠️</span> {error}
          </div>
        )}
        {success && (
          <div className="bg-gray-900 text-white px-6 py-4 rounded-2xl shadow-2xl animate-fadeUp flex items-center gap-3 border border-gray-700">
            <span className="text-green-400">✓</span> {success}
          </div>
        )}
      </div>

      <div className="grid md:grid-cols-2 gap-8">
        
        <section className="bg-white p-8 rounded-[32px] border border-gray-100 shadow-sm hover:shadow-xl transition-shadow duration-500">
          <div className="mb-6">
            <div className="w-12 h-12 bg-red-50 text-red-600 rounded-2xl flex items-center justify-center text-xl mb-4">📂</div>
            <h2 className="text-xl font-bold text-gray-800">Create a board</h2>
            <p className="text-sm text-gray-500">Group your pins by theme.</p>
          </div>

          <div className="space-y-4">
            <input
              className={inputStyle}
              placeholder="Board Name (e.g., Minimalist Design)"
              value={boardForm.title}
              onChange={e => setBoardForm({ ...boardForm, title: e.target.value })}
            />
            <input
              className={inputStyle}
              placeholder="Category (Art, Tech, Travel...)"
              value={boardForm.category}
              onChange={e => setBoardForm({ ...boardForm, category: e.target.value })}
            />
            <button 
              className="w-full py-3.5 bg-gray-900 hover:bg-black text-white font-bold rounded-full transition-all active:scale-95 shadow-lg shadow-gray-200"
              onClick={handleCreateBoard}
            >
              Create board
            </button>
          </div>
        </section>

        <section className="bg-white p-8 rounded-[32px] border border-gray-100 shadow-sm hover:shadow-xl transition-shadow duration-500">
          <div className="mb-6">
            <div className="w-12 h-12 bg-red-600 text-white rounded-2xl flex items-center justify-center text-xl mb-4">📌</div>
            <h2 className="text-xl font-bold text-gray-800">Add a pin</h2>
            <p className="text-sm text-gray-500">Publish a new idea to a board.</p>
          </div>

          <div className="space-y-4">
            <input
              className={inputStyle}
              placeholder="Pin Title"
              value={pinForm.title}
              onChange={e => setPinForm({ ...pinForm, title: e.target.value })}
            />
            <div className="relative">
              <select
                className={`${inputStyle} appearance-none cursor-pointer`}
                value={pinForm.board_id}
                onChange={e => setPinForm({ ...pinForm, board_id: e.target.value })}
              >
                <option value="">Select a board</option>
                {boards.map(b => (
                  <option key={b.id} value={b.id}>{b.title}</option>
                ))}
              </select>
              <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400">
                ▼
              </div>
            </div>
            <input 
  type="file" 
  accept="image/*"
  onChange={(e) => setFile(e.target.files[0])}
  className="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-red-50 file:text-red-700 hover:file:bg-red-100"
/>
            <button 
              className="w-full py-3.5 bg-red-600 hover:bg-red-700 text-white font-bold rounded-full transition-all active:scale-95 shadow-lg shadow-red-100"
              onClick={handleCreatePin}
            >
              Publish pin
            </button>
          </div>
        </section>

      </div>

    </div>
  );
}

export default Create;