import { useState } from 'react';
import axios from 'axios';
const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  async function submit(event) {
    event.preventDefault(); setBusy(true); setError('');
    try {
      const { data } = await axios.post(`${API}/login`, { username, password });
      onLogin(data.token, data.user);
    } catch (err) { setError(err.response?.data?.detail || 'Sign in failed'); }
    finally { setBusy(false); }
  }
  return <main style={{minHeight:'100vh',display:'grid',placeItems:'center',background:'#f3f6fa'}}>
    <form onSubmit={submit} style={{background:'white',padding:32,borderRadius:12,width:'min(420px,90vw)',boxShadow:'0 8px 32px #0001'}}>
      <h1>Sign in</h1><p>Access your manufacturing scenarios and SOTA data.</p>
      <label htmlFor="login-username">Username</label>
      <input id="login-username" autoComplete="username" value={username} onChange={e=>setUsername(e.target.value)} required style={{display:'block',width:'100%',margin:'8px 0 16px',padding:10}} />
      <label htmlFor="login-password">Password</label>
      <input id="login-password" type="password" autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)} required style={{display:'block',width:'100%',margin:'8px 0 16px',padding:10}} />
      {error && <p role="alert" style={{color:'#a00020'}}>{error}</p>}
      <button type="submit" disabled={busy} style={{padding:'10px 24px'}}>{busy?'Signing in…':'Sign in'}</button>
    </form>
  </main>;
}
