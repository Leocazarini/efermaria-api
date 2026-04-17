import logging
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .models import UserProfile
from .serializers import RegisterSerializer, UserProfileSerializer, ChangePasswordSerializer, UserAdminSerializer, UserManageSerializer

logger = logging.getLogger('authentication.views')

User = get_user_model()


class RegisterView(APIView):
    """POST /api/auth/register/ — Criação de novo usuário (inativo até aprovação)."""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"Novo usuário registrado (pendente de aprovação): {user.username}")
            return Response(
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'detail': 'Usuário criado com sucesso. Aguardando aprovação do administrador.',
                },
                status=status.HTTP_201_CREATED,
            )
        logger.warning(f"Falha no registro: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """GET /api/auth/me/ — Perfil do usuário autenticado."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ChangePasswordView(APIView):
    """POST /api/auth/change-password/ — Troca de senha."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        old_password = serializer.validated_data['old_password']

        if not user.check_password(old_password):
            return Response(
                {'old_password': 'Senha atual incorreta.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data['new_password'])
        user.save()
        logger.info(f"Senha alterada para o usuário: {user.username}")
        return Response({'detail': 'Senha alterada com sucesso.'}, status=status.HTTP_200_OK)


class UsersListView(APIView):
    """GET /api/auth/users/ — Lista todos os usuários (admin)."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.all().order_by('is_active', 'date_joined')
        serializer = UserAdminSerializer(users, many=True)
        return Response(serializer.data)


class PendingUsersView(APIView):
    """GET /api/auth/users/pending/ — Lista usuários aguardando aprovação."""
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = User.objects.filter(is_active=False).order_by('date_joined')
        serializer = UserAdminSerializer(users, many=True)
        return Response(serializer.data)


class ApproveUserView(APIView):
    """POST /api/auth/users/<pk>/approve/ — Aprova um usuário pendente."""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({'detail': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        if user.is_active:
            return Response({'detail': 'Usuário já está ativo.'}, status=status.HTTP_400_BAD_REQUEST)

        user.is_active = True
        user.save(update_fields=['is_active'])
        UserProfile.objects.update_or_create(user=user, defaults={'approved_at': timezone.now()})
        logger.info(f"Usuário '{user.username}' aprovado por '{request.user.username}'")
        return Response(
            {'detail': f"Usuário '{user.username}' aprovado com sucesso."},
            status=status.HTTP_200_OK,
        )


class UserManageView(APIView):
    """PATCH /api/auth/users/<pk>/ — Atualiza is_active/is_staff. DELETE — remove usuário."""
    permission_classes = [IsAdminUser]

    def _get_user(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            return None

    def patch(self, request, pk):
        user = self._get_user(pk)
        if not user:
            return Response({'detail': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if user == request.user:
            return Response({'detail': 'Você não pode alterar seu próprio status.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserManageSerializer(user, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        # Se está sendo desativado, garante que approved_at esteja gravado
        # (prova que o usuário já foi ativo em algum momento)
        if request.data.get('is_active') is False:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if not profile.approved_at:
                profile.approved_at = timezone.now()
                profile.save(update_fields=['approved_at'])
        logger.info(f"Usuário '{user.username}' atualizado por '{request.user.username}': {request.data}")
        return Response(UserAdminSerializer(user).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        user = self._get_user(pk)
        if not user:
            return Response({'detail': 'Usuário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        if user == request.user:
            return Response({'detail': 'Você não pode excluir sua própria conta.'}, status=status.HTTP_400_BAD_REQUEST)

        username = user.username
        user.delete()
        logger.info(f"Usuário '{username}' excluído por '{request.user.username}'")
        return Response(status=status.HTTP_204_NO_CONTENT)
