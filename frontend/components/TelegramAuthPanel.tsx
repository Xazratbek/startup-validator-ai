'use client';

import { useMemo, useState } from 'react';
import { apiFetch } from '@/lib/api';
import { setTokens } from '@/lib/auth';

const txt = {
  uz: {
    title: 'Telegram orqali kirish',
    desc: 'Bot orqali 6 xonali kod oling va saytda kiriting.',
    start: 'Telegram botga ulanish',
    codeLabel: '6 xonali kod',
    verify: 'Kodni tasdiqlash',
    waiting: 'Botda /start bering, keyin kod keladi.',
    openBot: 'Botni ochish',
  },
  en: {
    title: 'Login with Telegram',
    desc: 'Get a 6-digit code from bot and enter it on the website.',
    start: 'Connect Telegram bot',
    codeLabel: '6-digit code',
    verify: 'Verify code',
    waiting: 'Send /start in bot, then receive code.',
    openBot: 'Open bot',
  },
};

export function TelegramAuthPanel() {
  const [language, setLanguage] = useState<'uz' | 'en'>('uz');
  const [sessionToken, setSessionToken] = useState('');
  const [botUrl, setBotUrl] = useState('');
  const [code, setCode] = useState('');
  const [message, setMessage] = useState('');

  const t = useMemo(() => txt[language], [language]);

  async function start() {
    setMessage('');
    const data = await apiFetch('/auth/telegram/start', {
      method: 'POST',
      body: JSON.stringify({ language }),
    });
    setSessionToken(data.session_token);
    setBotUrl(data.bot_url);
    if (data.bot_url) window.open(data.bot_url, '_blank');
    setMessage(t.waiting);
  }

  async function verify() {
    const data = await apiFetch('/auth/telegram/verify', {
      method: 'POST',
      body: JSON.stringify({ session_token: sessionToken, code }),
    });
    setTokens(data.access, data.refresh);
    window.location.href = '/dashboard';
  }

  return <div className="card stack auth-card reveal d2">
    <div className="split">
      <button className={`btn secondary`} onClick={()=>setLanguage('uz')}>O'zbekcha</button>
      <button className={`btn secondary`} onClick={()=>setLanguage('en')}>English</button>
    </div>
    <h2>{t.title}</h2>
    <p className="muted">{t.desc}</p>
    <button className="btn" onClick={start}>{t.start}</button>
    {botUrl ? <a className="bot-link" href={botUrl} target="_blank">↗ {t.openBot}</a> : null}
    {sessionToken ? <>
      <label>{t.codeLabel}</label>
      <input className="input" value={code} onChange={(e)=>setCode(e.target.value)} maxLength={6} />
      <button className="btn" onClick={verify}>{t.verify}</button>
    </> : null}
    {message ? <div className="muted">{message}</div> : null}
  </div>;
}
