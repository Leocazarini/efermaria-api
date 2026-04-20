import pytest
from django.contrib.auth import get_user_model
from authentication import services
from authentication.models import UserProfile

User = get_user_model()


# ------------------------------------------------------------------
# register_user
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_register_user_creates_inactive_user():
    user = services.register_user(
        username='nova.enfermeira',
        email='nova@enfermaria.com',
        password='SenhaSegura#2024',
        first_name='Nova',
        last_name='Enfermeira',
    )
    assert user.pk is not None
    assert user.is_active is False
    assert user.username == 'nova.enfermeira'


@pytest.mark.django_db
def test_register_user_sets_correct_fields():
    user = services.register_user(
        username='carlos.silva',
        email='carlos@enfermaria.com',
        password='SenhaSegura#2024',
        first_name='Carlos',
        last_name='Silva',
    )
    assert user.first_name == 'Carlos'
    assert user.last_name == 'Silva'
    assert user.email == 'carlos@enfermaria.com'


# ------------------------------------------------------------------
# get_active_nurse_names
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_get_active_nurse_names_returns_first_names():
    User.objects.create_user(username='ana.silva', password='x', first_name='Ana', is_active=True)
    User.objects.create_user(username='beta.costa', password='x', first_name='Beta', is_active=True)
    names = services.get_active_nurse_names()
    assert 'Ana' in names
    assert 'Beta' in names


@pytest.mark.django_db
def test_get_active_nurse_names_excludes_inactive():
    User.objects.create_user(username='ativa', password='x', first_name='Ativa', is_active=True)
    User.objects.create_user(username='inativa', password='x', first_name='Inativa', is_active=False)
    names = services.get_active_nurse_names()
    assert 'Ativa' in names
    assert 'Inativa' not in names


@pytest.mark.django_db
def test_get_active_nurse_names_excludes_admin():
    User.objects.create_user(username='admin', password='x', first_name='Admin', is_active=True)
    names = services.get_active_nurse_names()
    assert 'Admin' not in names


@pytest.mark.django_db
def test_get_active_nurse_names_deduplicates():
    User.objects.create_user(username='ana.silva', password='x', first_name='Ana Silva', is_active=True)
    User.objects.create_user(username='ana.costa', password='x', first_name='Ana Costa', is_active=True)
    names = services.get_active_nurse_names()
    assert names.count('Ana') == 1


@pytest.mark.django_db
def test_get_active_nurse_names_uses_username_when_no_first_name():
    User.objects.create_user(username='semfirstname', password='x', first_name='', is_active=True)
    names = services.get_active_nurse_names()
    assert 'semfirstname' in names


# ------------------------------------------------------------------
# get_all_users / get_pending_users
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_get_all_users_returns_all():
    User.objects.create_user(username='u1', password='x', is_active=True)
    User.objects.create_user(username='u2', password='x', is_active=False)
    users = services.get_all_users()
    usernames = list(users.values_list('username', flat=True))
    assert 'u1' in usernames
    assert 'u2' in usernames


@pytest.mark.django_db
def test_get_pending_users_returns_only_inactive():
    User.objects.create_user(username='ativo', password='x', is_active=True)
    User.objects.create_user(username='pendente', password='x', is_active=False)
    pending = services.get_pending_users()
    usernames = list(pending.values_list('username', flat=True))
    assert 'pendente' in usernames
    assert 'ativo' not in usernames


# ------------------------------------------------------------------
# approve_user
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_approve_user_activates_and_records_timestamp():
    user = User.objects.create_user(username='pendente', password='x', is_active=False)
    result, error, code = services.approve_user(user.pk, 'admin')
    assert error is None
    assert code == 200
    user.refresh_from_db()
    assert user.is_active is True
    profile = UserProfile.objects.get(user=user)
    assert profile.approved_at is not None


@pytest.mark.django_db
def test_approve_user_already_active_returns_400():
    user = User.objects.create_user(username='ativo', password='x', is_active=True)
    _, error, code = services.approve_user(user.pk, 'admin')
    assert code == 400
    assert error == 'Usuário já está ativo.'


@pytest.mark.django_db
def test_approve_user_not_found_returns_404():
    _, error, code = services.approve_user(99999, 'admin')
    assert code == 404
    assert error == 'Usuário não encontrado.'


# ------------------------------------------------------------------
# change_password
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_change_password_success():
    user = User.objects.create_user(username='enfermeira', password='SenhaAntiga#1')
    success, error = services.change_password(user, 'SenhaAntiga#1', 'SenhaNova#2')
    assert success is True
    assert error is None
    user.refresh_from_db()
    assert user.check_password('SenhaNova#2')


@pytest.mark.django_db
def test_change_password_wrong_old_password():
    user = User.objects.create_user(username='enfermeira', password='SenhaAntiga#1')
    success, error = services.change_password(user, 'SenhaErrada', 'SenhaNova#2')
    assert success is False
    assert error == 'Senha atual incorreta.'


# ------------------------------------------------------------------
# update_user
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_update_user_changes_is_staff():
    admin = User.objects.create_user(username='admin', password='x', is_staff=True)
    target = User.objects.create_user(username='enfermeira', password='x', is_staff=False)
    user, error, code = services.update_user(
        target.pk, {'is_staff': True}, requesting_user_pk=admin.pk, requesting_username='admin'
    )
    assert error is None
    assert code == 200
    target.refresh_from_db()
    assert target.is_staff is True


@pytest.mark.django_db
def test_update_user_cannot_modify_self():
    user = User.objects.create_user(username='admin', password='x', is_staff=True)
    _, error, code = services.update_user(
        user.pk, {'is_active': False}, requesting_user_pk=user.pk, requesting_username='admin'
    )
    assert code == 400
    assert 'próprio' in error


@pytest.mark.django_db
def test_update_user_not_found_returns_404():
    _, error, code = services.update_user(
        99999, {'is_active': False}, requesting_user_pk=1, requesting_username='admin'
    )
    assert code == 404


@pytest.mark.django_db
def test_update_user_deactivation_records_approved_at():
    admin = User.objects.create_user(username='admin', password='x', is_staff=True)
    target = User.objects.create_user(username='enfermeira', password='x', is_active=True)
    services.update_user(
        target.pk, {'is_active': False}, requesting_user_pk=admin.pk, requesting_username='admin'
    )
    profile = UserProfile.objects.get(user=target)
    assert profile.approved_at is not None


# ------------------------------------------------------------------
# delete_user
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_delete_user_removes_from_db():
    admin = User.objects.create_user(username='admin', password='x')
    target = User.objects.create_user(username='remover', password='x')
    success, error, code = services.delete_user(
        target.pk, requesting_user_pk=admin.pk, requesting_username='admin'
    )
    assert success is True
    assert error is None
    assert code == 204
    assert not User.objects.filter(username='remover').exists()


@pytest.mark.django_db
def test_delete_user_cannot_delete_self():
    user = User.objects.create_user(username='admin', password='x')
    success, error, code = services.delete_user(
        user.pk, requesting_user_pk=user.pk, requesting_username='admin'
    )
    assert success is False
    assert code == 400


@pytest.mark.django_db
def test_delete_user_not_found_returns_404():
    success, error, code = services.delete_user(
        99999, requesting_user_pk=1, requesting_username='admin'
    )
    assert success is False
    assert code == 404
