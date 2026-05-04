import React, { useState } from 'react';
import './Login.css';

const API = 'http://localhost:8000';

function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');
  const currentBoard = profile?.boards?.find(b => b.id === selectedBoard);

    const handleSubmit = async () => {
        setError('');
        try {
        if (isRegister) {
            const res = await fetch(`${API}/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(form)
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail);
            onLogin(data.token, data.user.id);
        } else {
            const formData = new FormData();
            formData.append('username', form.email);
            formData.append('password', form.password);
            const res = await fetch(`${API}/auth/login`, {
            method: 'POST',
            body: formData
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.detail);
            // Récupère le profil pour avoir l'id
            const meRes = await fetch(`${API}/users/me`, {
            headers: { Authorization: `Bearer ${data.access_token}` }
            });
            const me = await meRes.json();
            onLogin(data.access_token, me.id);
        }
        } catch (e) {
        setError(e.message);
        }
    };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2>{isRegister ? 'Create account' : 'Welcome back'}</h2>
        <p className="login-subtitle">
          {isRegister ? 'Join Dayfold today' : 'Sign in to your account'}
        </p>

        {isRegister && (
          <input
            className="login-input"
            placeholder="Username"
            value={form.username}
            onChange={e => setForm({ ...form, username: e.target.value })}
          />
        )}
        <input
          className="login-input"
          placeholder="Email"
          type="email"
          value={form.email}
          onChange={e => setForm({ ...form, email: e.target.value })}
        />
        <input
          className="login-input"
          placeholder="Password"
          type="password"
          value={form.password}
          onChange={e => setForm({ ...form, password: e.target.value })}
        />

        {error && <p className="login-error">{error}</p>}

        <button className="login-btn" onClick={handleSubmit}>
          {isRegister ? 'Register' : 'Login'}
        </button>

        <p className="login-switch">
          {isRegister ? 'Already have an account?' : "Don't have an account?"}
          <span onClick={() => setIsRegister(!isRegister)}>
            {isRegister ? ' Login' : ' Register'}
          </span>
        </p>
      </div>
    </div>
  );
}

export default Login;