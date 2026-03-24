from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    SignupSerializer,
    TelegramAuthStartSerializer,
    TelegramCodeVerifySerializer,
    TelegramWebhookSerializer,
    UserSerializer,
)
from .telegram_auth import TelegramAuthService


class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'user': UserSerializer(user).data,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            status=201,
        )


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)


class LogoutView(APIView):
    def post(self, request):
        token = request.data.get('refresh')
        if token:
            RefreshToken(token).blacklist()
        return Response({'status': 'ok'})


class TelegramAuthStartView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TelegramAuthStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = TelegramAuthService.create_session(serializer.validated_data['language'])
        return Response(
            {
                'session_token': session.session_token,
                'bot_url': TelegramAuthService.bot_url(session),
                'status': session.status,
            }
        )


class TelegramCodeVerifyView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TelegramCodeVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, error = TelegramAuthService.verify_code(
            serializer.validated_data['session_token'],
            serializer.validated_data['code'],
        )
        if error:
            return Response({'detail': error}, status=status.HTTP_400_BAD_REQUEST)
        refresh = RefreshToken.for_user(user)
        return Response({'access': str(refresh.access_token), 'refresh': str(refresh), 'user': UserSerializer(user).data})


class TelegramWebhookView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = TelegramWebhookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        TelegramAuthService.process_update(serializer.validated_data)
        return Response({'ok': True})
