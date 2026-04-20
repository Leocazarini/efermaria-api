import logging
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import UserProfile

logger = logging.getLogger('authentication.services')

User = get_user_model()


def register_user(username, email, password, first_name='', last_name=''):
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )
    user.is_active = False
    user.save(update_fields=['is_active'])
    logger.info(f"Novo usuário registrado (pendente de aprovação): {user.username}")
    return user


def get_active_nurse_names():
    users = User.objects.filter(is_active=True).exclude(username='admin').order_by('first_name', 'username')
    seen = set()
    names = []
    for user in users:
        name = user.first_name.split()[0] if user.first_name else user.username
        if name not in seen:
            seen.add(name)
            names.append(name)
    return names


def get_all_users():
    return User.objects.all().order_by('is_active', 'date_joined')


def get_pending_users():
    return User.objects.filter(is_active=False).order_by('date_joined')


def approve_user(pk, approved_by_username):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return None, 'Usuário não encontrado.', 404

    if user.is_active:
        return None, 'Usuário já está ativo.', 400

    user.is_active = True
    user.save(update_fields=['is_active'])
    UserProfile.objects.update_or_create(user=user, defaults={'approved_at': timezone.now()})
    logger.info(f"Usuário '{user.username}' aprovado por '{approved_by_username}'")
    return user, None, 200


def change_password(user, old_password, new_password):
    if not user.check_password(old_password):
        return False, 'Senha atual incorreta.'
    user.set_password(new_password)
    user.save()
    logger.info(f"Senha alterada para o usuário: {user.username}")
    return True, None


def update_user(pk, data, requesting_user_pk, requesting_username):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return None, 'Usuário não encontrado.', 404

    if pk == requesting_user_pk:
        return None, 'Você não pode alterar seu próprio status.', 400

    allowed_fields = {'is_active', 'is_staff'}
    update_fields = [f for f in data if f in allowed_fields]
    for field in update_fields:
        setattr(user, field, data[field])
    if update_fields:
        user.save(update_fields=update_fields)

    if data.get('is_active') is False:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if not profile.approved_at:
            profile.approved_at = timezone.now()
            profile.save(update_fields=['approved_at'])

    logger.info(f"Usuário '{user.username}' atualizado por '{requesting_username}': {data}")
    return user, None, 200


def delete_user(pk, requesting_user_pk, requesting_username):
    try:
        user = User.objects.get(pk=pk)
    except User.DoesNotExist:
        return False, 'Usuário não encontrado.', 404

    if pk == requesting_user_pk:
        return False, 'Você não pode excluir sua própria conta.', 400

    username = user.username
    user.delete()
    logger.info(f"Usuário '{username}' excluído por '{requesting_username}'")
    return True, None, 204
