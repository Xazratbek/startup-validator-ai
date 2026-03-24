from __future__ import annotations

import os
import secrets
from datetime import timedelta

import requests
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import TelegramAuthSession, TelegramProfile

User = get_user_model()


class TelegramAuthService:
    @staticmethod
    def create_session(language: str = 'uz') -> TelegramAuthSession:
        return TelegramAuthSession.objects.create(session_token=secrets.token_urlsafe(24), language=language)

    @staticmethod
    def bot_url(session: TelegramAuthSession) -> str:
        username = os.getenv('TELEGRAM_BOT_USERNAME', '').strip().lstrip('@')
        return f'https://t.me/{username}?start=auth_{session.session_token}' if username else ''

    @staticmethod
    def process_update(update: dict) -> None:
        message = update.get('message') or update.get('edited_message') or {}
        if not message:
            return
        from_user = message.get('from') or {}
        text = (message.get('text') or '').strip()
        tg_user_id = from_user.get('id')
        if not tg_user_id:
            return

        if text.startswith('/start'):
            payload = text.replace('/start', '').strip()
            if payload.startswith('auth_'):
                token = payload.replace('auth_', '', 1)
                TelegramAuthService._bind_session(token, from_user)
                return
            TelegramAuthService._send_message(
                tg_user_id,
                "Assalomu alaykum! Login uchun sayt ichidagi tugmani bosing.\n"
                "Hi! Use the website button to start login."
            )
            return

        active = TelegramAuthSession.objects.filter(
            telegram_user_id=tg_user_id,
            status=TelegramAuthSession.Status.WAITING_PROFILE,
        ).order_by('-updated_at').first()
        if active:
            TelegramAuthService._handle_profile_step(active, text, from_user)

    @staticmethod
    def verify_code(session_token: str, code: str):
        session = TelegramAuthSession.objects.filter(session_token=session_token).first()
        if not session:
            return None, 'Session topilmadi / Session not found.'
        if not session.code_is_valid(code):
            return None, 'Kod noto‘g‘ri yoki muddati tugagan / Invalid or expired code.'
        if not session.user:
            return None, 'Foydalanuvchi ulanmagan / User not linked.'
        session.status = TelegramAuthSession.Status.VERIFIED
        session.save(update_fields=['status', 'updated_at'])
        return session.user, None

    @staticmethod
    def _bind_session(token: str, tg_user: dict) -> None:
        session = TelegramAuthSession.objects.filter(session_token=token).first()
        if not session:
            TelegramAuthService._send_message(tg_user.get('id'), 'Sessiya topilmadi / Session not found.')
            return
        session.telegram_user_id = tg_user['id']
        session.save(update_fields=['telegram_user_id', 'updated_at'])

        profile = TelegramProfile.objects.filter(telegram_user_id=tg_user['id']).select_related('user').first()
        if profile:
            profile.telegram_username = tg_user.get('username', '')
            profile.first_name = tg_user.get('first_name', '')
            profile.last_name = tg_user.get('last_name', '')
            profile.save(update_fields=['telegram_username', 'first_name', 'last_name', 'updated_at'])
            session.user = profile.user
            TelegramAuthService._issue_code(session)
            return

        session.status = TelegramAuthSession.Status.WAITING_PROFILE
        session.save(update_fields=['status', 'updated_at'])
        TelegramAuthService._send_message(
            tg_user['id'],
            "Ro'yxatdan o'tish uchun ism familiyangizni yuboring.\n"
            "To register, send your full name."
        )

    @staticmethod
    def _handle_profile_step(session: TelegramAuthSession, text: str, tg_user: dict) -> None:
        if not session.entered_full_name:
            session.entered_full_name = text
            session.save(update_fields=['entered_full_name', 'updated_at'])
            TelegramAuthService._send_message(
                tg_user['id'],
                "Telefon raqamingizni yuboring (+998...).\n"
                "Send your phone number (+998...)."
            )
            return

        if not session.entered_phone:
            session.entered_phone = text
            fallback_username = f"tg_{tg_user['id']}"
            user = User.objects.filter(phone_number=text).first()
            if not user:
                email = f"{fallback_username}@telegram.local"
                user = User.objects.create_user(
                    username=fallback_username,
                    email=email,
                    password=secrets.token_urlsafe(16),
                    first_name=session.entered_full_name,
                    phone_number=text,
                    preferred_language=session.language,
                )
            profile, _ = TelegramProfile.objects.get_or_create(user=user, defaults={'telegram_user_id': tg_user['id']})
            profile.telegram_user_id = tg_user['id']
            profile.telegram_username = tg_user.get('username', '')
            profile.first_name = tg_user.get('first_name', '')
            profile.last_name = tg_user.get('last_name', '')
            profile.save()
            session.user = user
            TelegramAuthService._issue_code(session)

    @staticmethod
    def _issue_code(session: TelegramAuthSession) -> None:
        session.code = f"{secrets.randbelow(1000000):06d}"
        session.code_expires_at = timezone.now() + timedelta(minutes=5)
        session.status = TelegramAuthSession.Status.CODE_SENT
        session.save(update_fields=['code', 'code_expires_at', 'status', 'user', 'updated_at'])
        TelegramAuthService._send_message(
            session.telegram_user_id,
            f"Tasdiqlash kodingiz / Your verification code: {session.code}\n"
            "5 daqiqa ichida saytda kiriting. / Enter on website within 5 minutes."
        )

    @staticmethod
    def _send_message(chat_id: int, text: str) -> None:
        token = os.getenv('TELEGRAM_BOT_TOKEN', '').strip()
        if not token:
            return
        requests.post(
            f'https://api.telegram.org/bot{token}/sendMessage',
            json={'chat_id': chat_id, 'text': text},
            timeout=10,
        )
