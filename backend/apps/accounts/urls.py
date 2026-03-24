from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import SignupView, MeView, LogoutView
urlpatterns = [
    path('auth/signup', SignupView.as_view()),
    path('auth/login', TokenObtainPairView.as_view()),
    path('auth/refresh', TokenRefreshView.as_view()),
    path('auth/logout', LogoutView.as_view()),
    path('me', MeView.as_view()),
]
