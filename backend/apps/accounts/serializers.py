from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import TelegramAuthSession

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'password', 'first_name', 'last_name',
            'phone_number', 'organization_name', 'job_title', 'preferred_language',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'email', 'username', 'first_name', 'last_name', 'phone_number',
            'organization_name', 'job_title', 'preferred_language',
        ]


class TelegramAuthStartSerializer(serializers.Serializer):
    language = serializers.ChoiceField(choices=['uz', 'en'], default='uz')


class TelegramAuthStartResponseSerializer(serializers.Serializer):
    session_token = serializers.CharField()
    bot_url = serializers.CharField()
    status = serializers.CharField()


class TelegramCodeVerifySerializer(serializers.Serializer):
    session_token = serializers.CharField()
    code = serializers.RegexField(r'^\d{6}$')


class TelegramWebhookSerializer(serializers.Serializer):
    update_id = serializers.IntegerField()
    message = serializers.DictField(required=False)
    edited_message = serializers.DictField(required=False)
