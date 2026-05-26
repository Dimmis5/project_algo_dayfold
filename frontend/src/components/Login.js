import React, { useState } from 'react';

const API = 'http://localhost:8000';

function Login({ onLogin }) {
  const [isRegister, setIsRegister] = useState(false);
  const [form, setForm] = useState({ username: '', email: '', password: '' });
  const [error, setError] = useState('');

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
        if (!res.ok) throw new Error(data.detail || "Erreur lors de l'inscription");
        onLogin(data.token, data.user.id);
      } else {
        const formData = new FormData();
        // Note: ton backend semble attendre 'username' pour l'email au login
        formData.append('username', form.email); 
        formData.append('password', form.password);
        
        const res = await fetch(`${API}/auth/login`, {
          method: 'POST',
          body: formData
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || "Identifiants invalides");

        // Récupération des infos utilisateur
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
    <div className="flex flex-col items-center justify-center min-h-[80vh] px-4">
      <div className="w-full max-w-md p-10 bg-white rounded-[32px] shadow-2xl border border-gray-100 text-center">
        
        {/* Logo Dayfold */}
        <h1 className="text-3xl font-bold text-red-600 mb-2 tracking-tighter">Dayfold</h1>
        
        <h2 className="text-2xl font-semibold text-gray-800 mb-2">
          {isRegister ? 'Créez votre compte' : 'Bon retour parmi nous'}
        </h2>
        
        <p className="text-gray-500 mb-8">
          {isRegister ? 'Rejoignez la communauté Dayfold' : 'Connectez-vous pour explorer'}
        </p>

        <div className="space-y-3">
          {isRegister && (
            <input
              className="w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:border-red-400 focus:ring-0 outline-none transition-all placeholder:text-gray-400"
              placeholder="Nom d'utilisateur"
              value={form.username}
              onChange={e => setForm({ ...form, username: e.target.value })}
            />
          )}
          
          <input
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:border-red-400 focus:ring-0 outline-none transition-all placeholder:text-gray-400"
            placeholder="Email"
            type="email"
            value={form.email}
            onChange={e => setForm({ ...form, email: e.target.value })}
          />
          
          <input
            className="w-full px-4 py-3 border-2 border-gray-200 rounded-2xl focus:border-red-400 focus:ring-0 outline-none transition-all placeholder:text-gray-400"
            placeholder="Mot de passe"
            type="password"
            value={form.password}
            onChange={e => setForm({ ...form, password: e.target.value })}
          />
        </div>

        {error && (
          <p className="mt-4 text-sm font-medium text-red-500 bg-red-50 py-2 rounded-lg">
            ⚠️ {error}
          </p>
        )}

        <button 
          className="w-full py-3 mt-8 bg-red-600 hover:bg-red-700 text-white font-bold rounded-full text-lg transition-colors shadow-lg shadow-red-200"
          onClick={handleSubmit}
        >
          {isRegister ? "S'inscrire" : 'Se connecter'}
        </button>

        <div className="mt-8 pt-6 border-t border-gray-100">
          <p className="text-gray-600 text-sm">
            {isRegister ? 'Déjà membre ?' : 'Pas encore de compte ?'}
            <button 
              className="ml-2 font-bold text-gray-800 hover:underline"
              onClick={() => setIsRegister(!isRegister)}
            >
              {isRegister ? 'Connectez-vous' : 'Inscrivez-vous'}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;