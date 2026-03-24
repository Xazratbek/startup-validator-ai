import { TelegramAuthPanel } from '@/components/TelegramAuthPanel';

export default function Signup(){
  return <main className="auth-shell">
    <div className="hero auth-card reveal">
      <h1>Ro'yxatdan o'tish / Sign up</h1>
      <p className="muted">Telegram bot orqali avtomatik profil yaratiladi.</p>
    </div>
    <TelegramAuthPanel />
  </main>;
}
