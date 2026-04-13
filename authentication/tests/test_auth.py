"""
Testes de autenticação (TDD - fase vermelha).
Esses testes descrevem o comportamento esperado ANTES da implementação.
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
    """Cria um usuário de enfermeira válido no banco."""
    return User.objects.create_user(
        username='enfermeira.ana',
        email='ana@enfermaria.com',
        password='SenhaSegura#2024',
        first_name='Ana',
        last_name='Silva',
    )


# ------------------------------------------------------------------
# REGISTRO DE USUÁRIO
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_register_new_user(api_client):
    """Um novo usuário pode se registrar com email, username e senha."""
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


@pytest.mark.django_db
def test_register_fails_if_passwords_dont_match(api_client):
    """Registro falha se as senhas não baterem."""
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
    """Registro falha se a senha for fraca (só números, menos de 8 chars)."""
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
    """Registro falha se o username já existir."""
    payload = {
        'username': 'enfermeira.ana',  # já existe
        'email': 'outroemail@enfermaria.com',
        'password': 'SenhaSegura#2024',
        'password_confirm': 'SenhaSegura#2024',
    }
    response = api_client.post('/api/auth/register/', payload, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST


# ------------------------------------------------------------------
# LOGIN - OBTER TOKENS JWT
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
    """Login com senha errada retorna 401."""
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
# PROTEÇÃO DE ROTAS (utilizando rota de perfil como cobaio)
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_access_protected_route_without_token(api_client):
    """Sem token, rota protegida retorna 401."""
    response = api_client.get('/api/auth/me/')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_access_protected_route_with_valid_token(api_client, nurse_user):
    """Com token JWT válido, rota /me/ retorna os dados do usuário."""
    # Faz login para obter token
    login_response = api_client.post(
        '/api/auth/login/',
        {'username': 'enfermeira.ana', 'password': 'SenhaSegura#2024'},
        format='json'
    )
    token = login_response.data['access']

    # Injeta token no header e acessa /me/
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    response = api_client.get('/api/auth/me/')

    assert response.status_code == status.HTTP_200_OK
    assert response.data['username'] == 'enfermeira.ana'
    assert 'password' not in response.data


# ------------------------------------------------------------------
# REFRESH DO TOKEN
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_refresh_token_returns_new_access(api_client, nurse_user):
    """Usando o refresh_token, obtemos um novo access_token."""
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
# ALTERAÇÃO DE SENHA
# ------------------------------------------------------------------

@pytest.mark.django_db
def test_change_password_with_valid_token(api_client, nurse_user):
    """Usuário autenticado pode trocar sua própria senha."""
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

    # Confirma que o login agora funciona com a nova senha
    api_client.credentials()  # limpa token
    new_login = api_client.post(
        '/api/auth/login/',
        {'username': 'enfermeira.ana', 'password': 'NovaSenha#2025'},
        format='json'
    )
    assert new_login.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_change_password_fails_with_wrong_old_password(api_client, nurse_user):
    """Troca de senha falha se a senha atual estiver errada."""
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
