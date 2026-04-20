"""
Testes de integração — Jornadas de autenticação.

Jornadas de usuário cobertas:

  1. Registro de nova enfermeira
     Intenção: uma nova colaboradora acessa o sistema e cria sua conta.
     Fluxo técnico: POST /api/auth/register/ → RegisterView → register_user()
     → User criado com is_active=False; ela NÃO consegue logar até aprovação.

  2. Login e obtenção de tokens JWT
     Intenção: enfermeira aprovada quer acessar o sistema.
     Fluxo técnico: POST /api/auth/login/ → simplejwt TokenObtainPairView
     → Retorna {access, refresh}; access dura 8h, refresh dura 7d.

  3. Acesso a rotas protegidas
     Intenção: cliente usa o token recebido para consultar seu perfil.
     Fluxo técnico: GET /api/auth/me/ com header Authorization: Bearer <token>
     → MeView → UserProfileSerializer; sem token retorna 401.

  4. Renovação de token
     Intenção: após expirar o access token, cliente renova sem fazer login novamente.
     Fluxo técnico: POST /api/auth/token/refresh/ com {refresh} → novo access token.

  5. Troca de senha autenticada
     Intenção: enfermeira quer alterar sua senha por questão de segurança.
     Fluxo técnico: POST /api/auth/change-password/ → ChangePasswordView
     → change_password() valida senha atual antes de substituir.

  6. Fluxo de aprovação de usuário (admin)
     Intenção: administrador gerencia quem pode acessar o sistema.
     Fluxo técnico:
       GET  /api/auth/users/pending/      → lista pendentes (IsAdminUser)
       POST /api/auth/users/<pk>/approve/ → ativa usuário (IsAdminUser)
     Restrição: usuário comum recebe 403; sem token recebe 401.
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def nurse_user(db):
    """Cria um usuário de enfermeira ativo diretamente no banco (já aprovado)."""
    return User.objects.create_user(
        username='enfermeira.ana',
        email='ana@enfermaria.com',
        password='SenhaSegura#2024',
        first_name='Ana',
        last_name='Silva',
        is_active=True,
    )


@pytest.fixture
def admin_user(db):
    """Cria um usuário administrador (is_staff=True) ativo no banco."""
    return User.objects.create_user(
        username='admin',
        email='admin@enfermaria.com',
        password='AdminSeguro#2024',
        is_staff=True,
        is_active=True,
    )


@pytest.fixture
def admin_client(db, admin_user):
    """APIClient autenticado como administrador."""
    client = APIClient()
    response = client.post(
        '/api/auth/login/',
        {'username': 'admin', 'password': 'AdminSeguro#2024'},
        format='json',
    )
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client


# ------------------------------------------------------------------
# JORNADA 1 — Registro de nova enfermeira
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_register_new_user(api_client):
    """Um novo usuário pode se registrar — fica inativo até aprovação do admin."""
    payload = {
        'username': 'enfermeira.betina',
        'email': 'betina@enfermaria.com',
        'password': 'SenhaSegura#2024',
        'password_confirm': 'SenhaSegura#2024',
        'first_name': 'Betina',
        'last_name': 'Costa',
    }
    response = api_client.post('/api/auth/register/', payload, format='json')
    assert response.status_code == status.HTTP_201_CREATED
    assert 'id' in response.data
    assert 'password' not in response.data  # nunca expor senha
    assert 'detail' in response.data        # mensagem de pendência
    assert User.objects.get(username='enfermeira.betina').is_active is False


@pytest.mark.django_db
def test_register_fails_if_passwords_dont_match(api_client):
    """Registro falha se as senhas não baterem — RegisterSerializer valida antes de criar."""
    payload = {
        'username': 'enfermeira.x',
        'email': 'x@enfermaria.com',
        'password': 'SenhaSegura#2024',
        'password_confirm': 'SenhaErrada#2024',
    }
    response = api_client.post('/api/auth/register/', payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_fails_with_weak_password(api_client):
    """Registro falha se a senha for fraca — Django password validators aplicados no serializer."""
    payload = {
        'username': 'enfermeira.y',
        'email': 'y@enfermaria.com',
        'password': '12345',
        'password_confirm': '12345',
    }
    response = api_client.post('/api/auth/register/', payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_register_fails_with_duplicate_username(api_client, nurse_user):
    """Registro falha se o username já existir — IntegrityError convertida em 400."""
    payload = {
        'username': 'enfermeira.ana',  # já existe
        'email': 'outroemail@enfermaria.com',
        'password': 'SenhaSegura#2024',
        'password_confirm': 'SenhaSegura#2024',
    }
    response = api_client.post('/api/auth/register/', payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ------------------------------------------------------------------
# JORNADA 2 — Login e obtenção de tokens JWT
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_login_returns_access_and_refresh_tokens(api_client, nurse_user):
    """Login com credenciais corretas retorna access_token e refresh_token."""
    payload = {'username': 'enfermeira.ana', 'password': 'SenhaSegura#2024'}
    response = api_client.post('/api/auth/login/', payload, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data
    assert 'refresh' in response.data


@pytest.mark.django_db
def test_login_fails_with_wrong_password(api_client, nurse_user):
    """Login com senha errada retorna 401 — simplejwt rejeita credenciais inválidas."""
    payload = {'username': 'enfermeira.ana', 'password': 'SenhaErrada'}
    response = api_client.post('/api/auth/login/', payload, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_login_fails_with_nonexistent_user(api_client):
    """Login com usuário inexistente retorna 401."""
    payload = {'username': 'naoexiste', 'password': 'qualquercoisa'}
    response = api_client.post('/api/auth/login/', payload, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ------------------------------------------------------------------
# JORNADA 3 — Acesso a rotas protegidas
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_access_protected_route_without_token(api_client):
    """Sem token, rota protegida retorna 401 — IsAuthenticated aplicado na view."""
    response = api_client.get('/api/auth/me/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_access_protected_route_with_valid_token(api_client, nurse_user):
    """Com token JWT válido, /me/ retorna os dados do usuário sem expor senha."""
    login_response = api_client.post(
        '/api/auth/login/',
        {'username': 'enfermeira.ana', 'password': 'SenhaSegura#2024'},
        format='json'
    )
    token = login_response.data['access']

    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.get('/api/auth/me/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == 'enfermeira.ana'
    assert 'password' not in response.data


# ------------------------------------------------------------------
# JORNADA 4 — Renovação de token
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_refresh_token_returns_new_access(api_client, nurse_user):
    """Usando o refresh_token, obtemos um novo access_token sem refazer login."""
    login_response = api_client.post(
        '/api/auth/login/',
        {'username': 'enfermeira.ana', 'password': 'SenhaSegura#2024'},
        format='json'
    )
    refresh = login_response.data['refresh']

    response = api_client.post('/api/auth/token/refresh/', {'refresh': refresh}, format='json')
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data


# ------------------------------------------------------------------
# JORNADA 5 — Troca de senha autenticada
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_change_password_with_valid_token(api_client, nurse_user):
    """Usuário autenticado troca sua própria senha; nova senha passa a valer imediatamente."""
    login_response = api_client.post(
        '/api/auth/login/',
        {'username': 'enfermeira.ana', 'password': 'SenhaSegura#2024'},
        format='json'
    )
    token = login_response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    response = api_client.post('/api/auth/change-password/', {
        'old_password': 'SenhaSegura#2024',
        'new_password': 'NovaSenha#2025',
        'new_password_confirm': 'NovaSenha#2025',
    }, format='json')

    assert response.status_code == status.HTTP_200_OK

    api_client.credentials()
    new_login = api_client.post(
        '/api/auth/login/',
        {'username': 'enfermeira.ana', 'password': 'NovaSenha#2025'},
        format='json'
    )
    assert new_login.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_change_password_fails_with_wrong_old_password(api_client, nurse_user):
    """Troca de senha falha se a senha atual estiver errada — change_password() valida antes de substituir."""
    login_response = api_client.post(
        '/api/auth/login/',
        {'username': 'enfermeira.ana', 'password': 'SenhaSegura#2024'},
        format='json'
    )
    token = login_response.data['access']
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

    response = api_client.post('/api/auth/change-password/', {
        'old_password': 'SenhaErrada',
        'new_password': 'NovaSenha#2025',
        'new_password_confirm': 'NovaSenha#2025',
    }, format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ------------------------------------------------------------------
# JORNADA 6 — Fluxo de aprovação de usuário (admin)
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_registered_user_cannot_login_before_approval(api_client):
    """Usuário recém-registrado não consegue fazer login — is_active=False bloqueia autenticação JWT."""
    api_client.post('/api/auth/register/', {
        'username': 'pendente',
        'email': 'pendente@enfermaria.com',
        'password': 'SenhaSegura#2024',
        'password_confirm': 'SenhaSegura#2024',
    }, format='json')

    response = api_client.post(
        '/api/auth/login/',
        {'username': 'pendente', 'password': 'SenhaSegura#2024'},
        format='json',
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_admin_can_list_pending_users(admin_client):
    """Administrador lista usuários pendentes — GET /users/pending/ exige IsAdminUser."""
    User.objects.create_user(username='p1', password='SenhaSegura#2024', is_active=False)
    User.objects.create_user(username='p2', password='SenhaSegura#2024', is_active=False)

    response = admin_client.get('/api/auth/users/pending/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert all(u['is_active'] is False for u in response.data)


@pytest.mark.django_db
def test_non_admin_cannot_list_pending_users(api_client, nurse_user):
    """Usuário comum recebe 403 ao tentar listar pendentes — IsAdminUser aplicado."""
    login = api_client.post(
        '/api/auth/login/',
        {'username': 'enfermeira.ana', 'password': 'SenhaSegura#2024'},
        format='json',
    )
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}')

    response = api_client.get('/api/auth/users/pending/')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_admin_can_approve_user(admin_client):
    """Administrador aprova um usuário pendente — approve_user() seta is_active=True."""
    pending = User.objects.create_user(username='pendente', password='SenhaSegura#2024', is_active=False)

    response = admin_client.post(f'/api/auth/users/{pending.pk}/approve/')
    assert response.status_code == status.HTTP_200_OK

    pending.refresh_from_db()
    assert pending.is_active is True


@pytest.mark.django_db
def test_approved_user_can_login(api_client, admin_client):
    """Após aprovação pelo admin, o usuário consegue fazer login normalmente."""
    pending = User.objects.create_user(username='pendente', password='SenhaSegura#2024', is_active=False)

    admin_client.post(f'/api/auth/users/{pending.pk}/approve/')

    response = api_client.post(
        '/api/auth/login/',
        {'username': 'pendente', 'password': 'SenhaSegura#2024'},
        format='json',
    )
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data


@pytest.mark.django_db
def test_approve_already_active_user_returns_400(admin_client, nurse_user):
    """Tentar aprovar usuário já ativo retorna 400 — approve_user() verifica estado atual."""
    response = admin_client.post(f'/api/auth/users/{nurse_user.pk}/approve/')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_approve_nonexistent_user_returns_404(admin_client):
    """pk inexistente na rota de aprovação retorna 404."""
    response = admin_client.post('/api/auth/users/99999/approve/')
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_non_admin_cannot_approve_user(api_client, nurse_user):
    """Usuário comum recebe 403 ao tentar aprovar — IsAdminUser protege o endpoint."""
    pending = User.objects.create_user(username='pendente', password='SenhaSegura#2024', is_active=False)

    login = api_client.post(
        '/api/auth/login/',
        {'username': 'enfermeira.ana', 'password': 'SenhaSegura#2024'},
        format='json',
    )
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}')

    response = api_client.post(f'/api/auth/users/{pending.pk}/approve/')
    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_unauthenticated_cannot_access_approval_endpoints(api_client):
    """Requisições sem token não acessam os endpoints de aprovação — retornam 401."""
    pending = User.objects.create_user(username='pendente', password='SenhaSegura#2024', is_active=False)

    assert api_client.get('/api/auth/users/pending/').status_code == status.HTTP_401_UNAUTHORIZED
    assert api_client.post(f'/api/auth/users/{pending.pk}/approve/').status_code == status.HTTP_401_UNAUTHORIZED
