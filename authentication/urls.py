from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, MeView, ChangePasswordView

urlpatterns = [
    # Registro
    path('register/', RegisterView.as_view(), name='auth-register'),

    # Login (JWT): retorna access + refresh tokens
    path('login/', TokenObtainPairView.as_view(), name='auth-login'),

    # Refresh do token de acesso
    path('token/refresh/', TokenRefreshView.as_view(), name='auth-token-refresh'),

    # Perfil do usuário autenticado
    path('me/', MeView.as_view(), name='auth-me'),

    # Troca de senha
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
]
