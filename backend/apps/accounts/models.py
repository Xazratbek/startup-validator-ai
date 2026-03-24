from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=32, blank=True)
    organization_name = models.CharField(max_length=255, blank=True)
    job_title = models.CharField(max_length=255, blank=True)
    preferred_language = models.CharField(max_length=8, default='uz')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class TelegramProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_profile')
    telegram_user_id = models.BigIntegerField(unique=True)
    telegram_username = models.CharField(max_length=255, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class TelegramAuthSession(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        WAITING_PROFILE = 'WAITING_PROFILE', 'Waiting profile'
        CODE_SENT = 'CODE_SENT', 'Code sent'
        VERIFIED = 'VERIFIED', 'Verified'
        EXPIRED = 'EXPIRED', 'Expired'

    session_token = models.CharField(max_length=64, unique=True)
    language = models.CharField(max_length=8, default='uz')
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.PENDING)
    telegram_user_id = models.BigIntegerField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='telegram_auth_sessions')
    code = models.CharField(max_length=6, blank=True)
    code_expires_at = models.DateTimeField(null=True, blank=True)
    entered_full_name = models.CharField(max_length=255, blank=True)
    entered_phone = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def code_is_valid(self, value: str) -> bool:
        return self.code == value and self.code_expires_at and timezone.now() <= self.code_expires_at
