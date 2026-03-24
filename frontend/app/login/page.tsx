'use client';

import { useState } from 'react';
import { apiFetch } from '@/lib/api';
import { setTokens } from '@/lib/auth';

export default function Login() {
  const [email, setEmail] = useState('demo@founderos.dev');
  const [password, setPassword] = useState('demo12345');
  const [error, setError] = useState('');

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    try {
      const data = await apiFetch('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
      setTokens(data.access, data.refresh);
      window.location.href = '/dashboard';
    } catch (err: any) {
      setError(err.message || 'Login failed');
    }
  }

  return <main className="container stack"><h1>Login</h1><form className="card stack" onSubmit={submit}><input className="input" value={email} onChange={e=>setEmail(e.target.value)} /><input className="input" type="password" value={password} onChange={e=>setPassword(e.target.value)} /><button className="btn" type="submit">Login</button>{error ? <div className="muted">{error}</div> : null}</form></main>;
}
