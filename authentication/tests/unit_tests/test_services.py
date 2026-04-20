"""
Testes unitários de authentication/services.py.

Contratos documentados aqui:

  register_user(username, email, password, first_name, last_name)
    → Cria User com is_active=False aguardando aprovação do admin.
    → Persiste todos os campos fornecidos; nunca expõe senha em texto claro.

  get_active_nurse_names()
    → Retorna lista de strings com o primeiro nome de cada usuário ativo.
    → Exclui o usuário 'admin' e usuários inativos.
    → Deduplica: dois usuários com o mesmo primeiro nome aparecem uma única vez.
    → Usa username como fallback quando first_name está vazio.

  get_all_users()
    → Retorna QuerySet de todos os usuários, ordenado por is_active e date_joined.

  get_pending_users()
    → Retorna QuerySet apenas de usuários com is_active=False.

  approve_user(pk, approved_by_username)
    → Ativa o usuário (is_active=True) e grava approved_at em UserProfile.
    → Retorna (user, None, 200) em sucesso.
    → Retorna (None, mensagem, 400) se o usuário já estiver ativo.
    → Retorna (None, mensagem, 404) se o pk não existir.

  change_password(user, old_password, new_password)
    → Valida old_password antes de substituir; retorna (False, mensagem) se incorreta.
    → Retorna (True, None) em sucesso; nova senha persiste e autentica na sequência.

  update_user(pk, data, requesting_user_pk, requesting_username)
    → Atualiza is_active e/ou is_staff conforme data fornecido.
    → Bloqueia auto-modificação: retorna (None, mensagem, 400) quando pk == requesting_user_pk.
    → Retorna (None, mensagem, 404) se pk não existir.
    → Ao desativar (is_active=False), grava approved_at em UserProfile se ainda não existir.

  delete_user(pk, requesting_user_pk, requesting_username)
    → Remove o usuário do banco; retorna (True, None, 204).
    → Bloqueia auto-exclusão: retorna (False, mensagem, 400) quando pk == requesting_user_pk.
    → Retorna (False, mensagem, 404) se pk não existir.
"""
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
    """Novo usuário é criado com is_active=False — nunca pode logar antes da aprovação."""
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
    """Todos os campos opcionais fornecidos são persistidos corretamente."""
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
    """Retorna o primeiro nome de cada usuário ativo."""
    User.objects.create_user(username='ana.silva', password='x', first_name='Ana', is_active=True)
    User.objects.create_user(username='beta.costa', password='x', first_name='Beta', is_active=True)
    names = services.get_active_nurse_names()
    assert 'Ana' in names
    assert 'Beta' in names


@pytest.mark.django_db
def test_get_active_nurse_names_excludes_inactive():
    """Usuários inativos não aparecem na lista."""
    User.objects.create_user(username='ativa', password='x', first_name='Ativa', is_active=True)
    User.objects.create_user(username='inativa', password='x', first_name='Inativa', is_active=False)
    names = services.get_active_nurse_names()
    assert 'Ativa' in names
    assert 'Inativa' not in names


@pytest.mark.django_db
def test_get_active_nurse_names_excludes_admin():
    """O usuário 'admin' é excluído mesmo estando ativo."""
    User.objects.create_user(username='admin', password='x', first_name='Admin', is_active=True)
    names = services.get_active_nurse_names()
    assert 'Admin' not in names


@pytest.mark.django_db
def test_get_active_nurse_names_deduplicates():
    """Dois usuários com o mesmo primeiro nome resultam em apenas uma entrada."""
    User.objects.create_user(username='ana.silva', password='x', first_name='Ana Silva', is_active=True)
    User.objects.create_user(username='ana.costa', password='x', first_name='Ana Costa', is_active=True)
    names = services.get_active_nurse_names()
    assert names.count('Ana') == 1


@pytest.mark.django_db
def test_get_active_nurse_names_uses_username_when_no_first_name():
    """Quando first_name está vazio, username é usado como identificador."""
    User.objects.create_user(username='semfirstname', password='x', first_name='', is_active=True)
    names = services.get_active_nurse_names()
    assert 'semfirstname' in names


# ------------------------------------------------------------------
# get_all_users / get_pending_users
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_get_all_users_returns_all():
    """Retorna todos os usuários independentemente do status."""
    User.objects.create_user(username='u1', password='x', is_active=True)
    User.objects.create_user(username='u2', password='x', is_active=False)
    users = services.get_all_users()
    usernames = list(users.values_list('username', flat=True))
    assert 'u1' in usernames
    assert 'u2' in usernames


@pytest.mark.django_db
def test_get_pending_users_returns_only_inactive():
    """Retorna somente usuários com is_active=False."""
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
    """Aprovação ativa o usuário e registra o momento em UserProfile.approved_at."""
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
    """Tentar aprovar um usuário já ativo retorna 400 com mensagem de erro."""
    user = User.objects.create_user(username='ativo', password='x', is_active=True)
    _, error, code = services.approve_user(user.pk, 'admin')
    assert code == 400
    assert error == 'Usuário já está ativo.'


@pytest.mark.django_db
def test_approve_user_not_found_returns_404():
    """pk inexistente retorna 404 com mensagem de erro."""
    _, error, code = services.approve_user(99999, 'admin')
    assert code == 404
    assert error == 'Usuário não encontrado.'


# ------------------------------------------------------------------
# change_password
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_change_password_success():
    """Senha válida é substituída; nova senha autentica na sequência."""
    user = User.objects.create_user(username='enfermeira', password='SenhaAntiga#1')
    success, error = services.change_password(user, 'SenhaAntiga#1', 'SenhaNova#2')
    assert success is True
    assert error is None
    user.refresh_from_db()
    assert user.check_password('SenhaNova#2')


@pytest.mark.django_db
def test_change_password_wrong_old_password():
    """Senha atual incorreta retorna (False, mensagem) sem alterar a senha."""
    user = User.objects.create_user(username='enfermeira', password='SenhaAntiga#1')
    success, error = services.change_password(user, 'SenhaErrada', 'SenhaNova#2')
    assert success is False
    assert error == 'Senha atual incorreta.'


# ------------------------------------------------------------------
# update_user
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_update_user_changes_is_staff():
    """Campo is_staff é atualizado com sucesso quando solicitado por outro usuário."""
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
    """Auto-modificação é bloqueada com 400 para evitar que admin se desative acidentalmente."""
    user = User.objects.create_user(username='admin', password='x', is_staff=True)
    _, error, code = services.update_user(
        user.pk, {'is_active': False}, requesting_user_pk=user.pk, requesting_username='admin'
    )
    assert code == 400
    assert 'próprio' in error


@pytest.mark.django_db
def test_update_user_not_found_returns_404():
    """pk inexistente retorna 404."""
    _, error, code = services.update_user(
        99999, {'is_active': False}, requesting_user_pk=1, requesting_username='admin'
    )
    assert code == 404


@pytest.mark.django_db
def test_update_user_deactivation_records_approved_at():
    """Ao desativar um usuário, approved_at é preenchido em UserProfile se ainda não existia."""
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
    """Usuário alvo é removido do banco; retorna (True, None, 204)."""
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
    """Auto-exclusão é bloqueada com 400."""
    user = User.objects.create_user(username='admin', password='x')
    success, error, code = services.delete_user(
        user.pk, requesting_user_pk=user.pk, requesting_username='admin'
    )
    assert success is False
    assert code == 400


@pytest.mark.django_db
def test_delete_user_not_found_returns_404():
    """pk inexistente retorna (False, mensagem, 404)."""
    success, error, code = services.delete_user(
        99999, requesting_user_pk=1, requesting_username='admin'
    )
    assert success is False
    assert code == 404
