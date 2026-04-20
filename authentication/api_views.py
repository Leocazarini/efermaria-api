import logging
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from .serializers import (
    RegisterSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    UserAdminSerializer,
    UserManageSerializer,
)
from . import services

logger = logging.getLogger('authentication.api_views')


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Falha no registro: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        user = services.register_user(
            username=data['username'],
            email=data.get('email', ''),
            password=data['password'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
        )
        return Response(
            {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'detail': 'Usuário criado com sucesso. Aguardando aprovação do administrador.',
            },
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        success, error = services.change_password(
            request.user,
            old_password=data['old_password'],
            new_password=data['new_password'],
        )
        if not success:
            return Response({'old_password': error}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'detail': 'Senha alterada com sucesso.'})


class NursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(services.get_active_nurse_names())


class UsersListView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = services.get_all_users()
        serializer = UserAdminSerializer(users, many=True)
        return Response(serializer.data)


class PendingUsersView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = services.get_pending_users()
        serializer = UserAdminSerializer(users, many=True)
        return Response(serializer.data)


class ApproveUserView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        user, error, http_status = services.approve_user(pk, request.user.username)
        if error:
            return Response({'detail': error}, status=http_status)
        return Response(
            {'detail': f"Usuário '{user.username}' aprovado com sucesso."},
            status=status.HTTP_200_OK,
        )


class UserManageView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        serializer = UserManageSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user, error, http_status = services.update_user(
            pk,
            data=serializer.validated_data,
            requesting_user_pk=request.user.pk,
            requesting_username=request.user.username,
        )
        if error:
            return Response({'detail': error}, status=http_status)
        return Response(UserAdminSerializer(user).data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        success, error, http_status = services.delete_user(
            pk,
            requesting_user_pk=request.user.pk,
            requesting_username=request.user.username,
        )
        if not success:
            return Response({'detail': error}, status=http_status)
        return Response(status=status.HTTP_204_NO_CONTENT)
