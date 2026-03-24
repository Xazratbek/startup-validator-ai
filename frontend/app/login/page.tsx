import { TelegramAuthPanel } from '@/components/TelegramAuthPanel';

export default function Login() {
  return <main className="auth-shell">
    <div className="hero auth-card reveal">
      <h1>Founder Validation OS</h1>
      <p className="muted">Tizimga kirish / Sign in</p>
    </div>
    <TelegramAuthPanel />
  </main>;
}
