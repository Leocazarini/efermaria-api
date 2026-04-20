"""
Testes de integração — Jornadas de relatórios e estatísticas.

Jornadas de usuário cobertas:

  1. Geração de relatório de atendimentos por período
     Intenção: coordenador da enfermaria precisa consultar todos os atendimentos
     de um período específico para análise ou prestação de contas.
     Fluxo técnico: GET /api/v1/reports/appointments/?date_begin=&date_end=&infirmaries=&search=
     → AppointmentReportView → get_all_appointments()
     → Retorna lista unificada (alunos + funcionários + visitantes) filtrada e ordenada.
     → 400 se date_begin ausente; [] se enfermaria sem registros no período.

  2. Consulta de estatísticas globais da enfermaria
     Intenção: coordenador visualiza o dashboard com totais do ano, do dia e
     ranking de enfermeiras para acompanhar a produtividade da equipe.
     Fluxo técnico: GET /api/v1/reports/stats/
     → StatsView → get_total_appointments_current_year() + get_total_appointments_today()
                  + get_nurse_appointments_current_year() + get_monthly_appointments_current_year()
     → Retorna {total_current_year, total_today, nurses, monthly_counts, recent_appointments}.

  3. Consulta de estatísticas por enfermaria
     Intenção: gestor compara o volume de atendimentos de diferentes unidades.
     Fluxo técnico: GET /api/v1/reports/stats/infirmary/<name>/
     → InfirmaryStatsView → get_total_appointments_infirmary_current_year() + _today()
     → Retorna {infirmary, total_current_year, total_today}.
     → Enfermaria inexistente retorna contadores zerados (não 404).

  Restrição comum: todos os endpoints exigem token JWT (IsAuthenticated).
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from patients.models import ClassGroup, Student, Department, Employee
from appointments.models import StudentAppointment, EmployeeAppointment

User = get_user_model()

BASE = '/api/v1/reports'


# ──────────────────────────────────────────────
# Fixtures compartilhadas
# ──────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(db):
    """APIClient autenticado via JWT para uso nos testes de integração."""
    user = User.objects.create_user(username='testuser', password='Pass1234!')
    client = APIClient()
    response = client.post(
        '/api/auth/login/',
        {'username': 'testuser', 'password': 'Pass1234!'},
        format='json',
    )
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client


@pytest.fixture
def class_group(db):
    return ClassGroup.objects.create(id='CG1', name='9A', segment='Fundamental', director='Dir. Silva')


@pytest.fixture
def student(db, class_group):
    return Student.objects.create(
        id='S1', name='Ana Lima', age=14, gender='Female',
        registry='STU001', class_group=class_group,
    )


@pytest.fixture
def department(db):
    return Department.objects.create(id='D1', name='TI', director='Dir. Costa')


@pytest.fixture
def employee(db, department):
    return Employee.objects.create(
        id='E1', name='Carlos Souza', age=35, gender='Male',
        registry='EMP001', department=department,
    )


@pytest.fixture
def student_appointment(db, student):
    return StudentAppointment.objects.create(
        student=student,
        infirmary='Enfermaria A',
        nurse='Enf. Joana',
        current_class='9A',
        date=timezone.now(),
        reason='Dor de cabeça',
        treatment='Dipirona',
        revaluation=False,
        contact_parents=False,
    )


@pytest.fixture
def employee_appointment(db, employee):
    return EmployeeAppointment.objects.create(
        employee=employee,
        infirmary='Enfermaria A',
        nurse='Enf. Joana',
        date=timezone.now(),
        reason='Pressão alta',
        treatment='Repouso',
        revaluation=False,
    )


def _today_range():
    """Retorna date_begin e date_end como strings ISO para o dia atual."""
    today = timezone.now().date()
    return today.isoformat(), today.isoformat()


# ──────────────────────────────────────────────
# Proteção de rotas
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestReportsAuth:
    """Todos os endpoints de relatório exigem JWT — sem token retorna 401."""

    def test_unauthenticated_appointments_returns_401(self, api_client):
        """Endpoints de relatórios requerem token JWT válido."""
        response = api_client.get(f'{BASE}/appointments/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_stats_returns_401(self, api_client):
        """Endpoint de estatísticas requer token JWT válido."""
        response = api_client.get(f'{BASE}/stats/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ──────────────────────────────────────────────
# Jornada 1 — Relatório de atendimentos por período
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestAppointmentsReport:
    """
    Coordenador consulta atendimentos de um período para análise ou prestação de contas.
    Fluxo: GET /appointments/?date_begin=&date_end=&infirmaries=&search=
    → get_all_appointments() → lista unificada ordenada por data decrescente.
    """

    def test_returns_200_with_valid_params(self, auth_client, student_appointment):
        """GET com parâmetros válidos retorna lista de atendimentos."""
        date_begin, date_end = _today_range()
        response = auth_client.get(
            f'{BASE}/appointments/',
            {'date_begin': date_begin, 'date_end': date_end, 'infirmaries': 'Enfermaria A'},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_returns_empty_list_when_no_match(self, auth_client, student_appointment):
        """GET com infirmaria sem registros retorna lista vazia — não retorna 404."""
        date_begin, date_end = _today_range()
        response = auth_client.get(
            f'{BASE}/appointments/',
            {'date_begin': date_begin, 'date_end': date_end, 'infirmaries': 'Sala Inexistente'},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_returns_400_when_missing_date_begin(self, auth_client):
        """GET sem date_begin retorna 400 — parâmetro obrigatório."""
        response = auth_client.get(
            f'{BASE}/appointments/',
            {'date_end': '2026-04-14', 'infirmaries': 'Enfermaria A'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_200_when_missing_infirmaries(self, auth_client, student_appointment):
        """GET sem infirmaries retorna 200 com todos os atendimentos do período."""
        date_begin, date_end = _today_range()
        response = auth_client.get(
            f'{BASE}/appointments/',
            {'date_begin': date_begin, 'date_end': date_end},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_search_term_filters_results(self, auth_client, student_appointment, employee_appointment):
        """GET com search filtra por termo livre em campos de texto dos atendimentos."""
        date_begin, date_end = _today_range()
        response = auth_client.get(
            f'{BASE}/appointments/',
            {'date_begin': date_begin, 'date_end': date_end, 'infirmaries': 'Enfermaria A', 'search': 'Dor'},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['reason'] == 'Dor de cabeça'

    def test_multiple_infirmaries_accepted(self, auth_client, student_appointment):
        """GET aceita múltiplas enfermarias como parâmetros repetidos na query string."""
        date_begin, date_end = _today_range()
        response = auth_client.get(
            f'{BASE}/appointments/?date_begin={date_begin}&date_end={date_end}'
            '&infirmaries=Enfermaria+A&infirmaries=Enfermaria+B'
        )
        assert response.status_code == status.HTTP_200_OK


# ──────────────────────────────────────────────
# Jornada 2 — Estatísticas globais da enfermaria
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestGlobalStats:
    """
    Coordenador acessa o dashboard com totais do ano, do dia e ranking de enfermeiras.
    Fluxo: GET /stats/ → contadores + monthly_counts (12 meses) + recent_appointments.
    """

    def test_returns_200_with_expected_keys(self, auth_client, student_appointment):
        """GET /stats/ retorna contadores globais com todas as chaves esperadas."""
        response = auth_client.get(f'{BASE}/stats/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_current_year' in response.data
        assert 'total_today' in response.data
        assert 'nurses' in response.data
        assert 'monthly_counts' in response.data
        assert 'recent_appointments' in response.data
        assert len(response.data['monthly_counts']) == 12

    def test_total_current_year_counts_appointments(self, auth_client, student_appointment, employee_appointment):
        """total_current_year inclui todos os tipos de atendimento do ano."""
        response = auth_client.get(f'{BASE}/stats/')
        assert response.data['total_current_year'] >= 2

    def test_returns_zero_when_no_appointments(self, auth_client, db):
        """Sem atendimentos, contadores retornam zero — endpoint não falha com banco vazio."""
        response = auth_client.get(f'{BASE}/stats/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_current_year'] == 0
        assert response.data['total_today'] == 0


# ──────────────────────────────────────────────
# Jornada 3 — Estatísticas por enfermaria
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestInfirmaryStats:
    """
    Gestor compara volume de atendimentos por unidade de enfermaria.
    Fluxo: GET /stats/infirmary/<name>/ → totais filtrados por enfermaria.
    Enfermaria inexistente retorna zeros, não 404.
    """

    def test_returns_200_with_expected_keys(self, auth_client, student_appointment):
        """GET /stats/infirmary/<name>/ retorna contadores com as chaves esperadas."""
        response = auth_client.get(f'{BASE}/stats/infirmary/Enfermaria A/')
        assert response.status_code == status.HTTP_200_OK
        assert 'infirmary' in response.data
        assert 'total_current_year' in response.data
        assert 'total_today' in response.data

    def test_counts_only_matching_infirmary(self, auth_client, student_appointment):
        """Contadores refletem apenas atendimentos da enfermaria solicitada."""
        response = auth_client.get(f'{BASE}/stats/infirmary/Enfermaria A/')
        assert response.data['total_current_year'] >= 1

    def test_returns_zero_for_unknown_infirmary(self, auth_client, student_appointment):
        """Enfermaria desconhecida retorna contadores zerados — não levanta erro."""
        response = auth_client.get(f'{BASE}/stats/infirmary/Sala Inexistente/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_current_year'] == 0
        assert response.data['total_today'] == 0
