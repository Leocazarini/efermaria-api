from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer para criação de novos usuários."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
        read_only_fields = ['id']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'As senhas não conferem.'})

        try:
            password_validation.validate_password(data['password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'password': list(e.messages)})

        return data


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para exibir o perfil do usuário autenticado (nunca expõe senha)."""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined', 'last_login']
        read_only_fields = fields


class UserAdminSerializer(serializers.ModelSerializer):
    """Serializer para listagem de usuários pelo administrador."""
    approved_at = serializers.SerializerMethodField()

    def get_approved_at(self, obj):
        try:
            return obj.profile.approved_at
        except Exception:
            return None

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'date_joined', 'last_login', 'approved_at']
        read_only_fields = fields


class UserManageSerializer(serializers.ModelSerializer):
    """Serializer para PATCH de is_active / is_staff pelo administrador."""
    class Meta:
        model = User
        fields = ['is_active', 'is_staff']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer para troca de senha autenticada."""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'As novas senhas não conferem.'}
            )
        try:
            password_validation.validate_password(data['new_password'])
        except DjangoValidationError as e:
            raise serializers.ValidationError({'new_password': list(e.messages)})
        return data
