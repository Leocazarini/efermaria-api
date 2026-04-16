import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from patients.models import ClassGroup, Student, Department, Employee, Visitor
from appointments.models import StudentAppointment, EmployeeAppointment, VisitorAppointment

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
# Autenticação
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestReportsAuth:
    def test_unauthenticated_appointments_returns_401(self, api_client):
        """Endpoints de relatórios requerem token JWT válido."""
        response = api_client.get(f'{BASE}/appointments/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_stats_returns_401(self, api_client):
        """Endpoint de estatísticas requer token JWT válido."""
        response = api_client.get(f'{BASE}/stats/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ──────────────────────────────────────────────
# GET /api/v1/reports/appointments/
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestAppointmentsReport:
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
        """GET com infirmaria sem registros retorna lista vazia."""
        date_begin, date_end = _today_range()
        response = auth_client.get(
            f'{BASE}/appointments/',
            {'date_begin': date_begin, 'date_end': date_end, 'infirmaries': 'Sala Inexistente'},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []

    def test_returns_400_when_missing_date_begin(self, auth_client):
        """GET sem date_begin retorna 400."""
        response = auth_client.get(
            f'{BASE}/appointments/',
            {'date_end': '2026-04-14', 'infirmaries': 'Enfermaria A'},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_returns_200_when_missing_infirmaries(self, auth_client, student_appointment):
        """GET sem infirmaries retorna 200 com todos os atendimentos (sem filtro de enfermaria)."""
        date_begin, date_end = _today_range()
        response = auth_client.get(
            f'{BASE}/appointments/',
            {'date_begin': date_begin, 'date_end': date_end},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_search_term_filters_results(self, auth_client, student_appointment, employee_appointment):
        """GET com search filtra por termo nos resultados."""
        date_begin, date_end = _today_range()
        response = auth_client.get(
            f'{BASE}/appointments/',
            {'date_begin': date_begin, 'date_end': date_end, 'infirmaries': 'Enfermaria A', 'search': 'Dor'},
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['reason'] == 'Dor de cabeça'

    def test_multiple_infirmaries_accepted(self, auth_client, student_appointment):
        """GET aceita múltiplas infirmarias como lista repetida."""
        date_begin, date_end = _today_range()
        response = auth_client.get(
            f'{BASE}/appointments/?date_begin={date_begin}&date_end={date_end}'
            '&infirmaries=Enfermaria+A&infirmaries=Enfermaria+B'
        )
        assert response.status_code == status.HTTP_200_OK


# ──────────────────────────────────────────────
# GET /api/v1/reports/stats/
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestGlobalStats:
    def test_returns_200_with_expected_keys(self, auth_client, student_appointment):
        """GET /stats/ retorna contadores globais com chaves esperadas."""
        response = auth_client.get(f'{BASE}/stats/')
        assert response.status_code == status.HTTP_200_OK
        assert 'total_current_year' in response.data
        assert 'total_today' in response.data
        assert 'nurses' in response.data
        assert 'monthly_counts' in response.data
        assert 'recent_appointments' in response.data
        assert len(response.data['monthly_counts']) == 12

    def test_total_current_year_counts_appointments(self, auth_client, student_appointment, employee_appointment):
        """total_current_year conta todos os atendimentos do ano."""
        response = auth_client.get(f'{BASE}/stats/')
        assert response.data['total_current_year'] >= 2

    def test_returns_zero_when_no_appointments(self, auth_client, db):
        """Sem atendimentos, os contadores retornam zero."""
        response = auth_client.get(f'{BASE}/stats/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_current_year'] == 0
        assert response.data['total_today'] == 0


# ──────────────────────────────────────────────
# GET /api/v1/reports/stats/infirmary/<name>/
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestInfirmaryStats:
    def test_returns_200_with_expected_keys(self, auth_client, student_appointment):
        """GET /stats/infirmary/<name>/ retorna contadores por enfermaria."""
        response = auth_client.get(f'{BASE}/stats/infirmary/Enfermaria A/')
        assert response.status_code == status.HTTP_200_OK
        assert 'infirmary' in response.data
        assert 'total_current_year' in response.data
        assert 'total_today' in response.data

    def test_counts_only_matching_infirmary(self, auth_client, student_appointment):
        """Contadores refletem apenas a enfermaria solicitada."""
        response = auth_client.get(f'{BASE}/stats/infirmary/Enfermaria A/')
        assert response.data['total_current_year'] >= 1

    def test_returns_zero_for_unknown_infirmary(self, auth_client, student_appointment):
        """Enfermaria desconhecida retorna contadores zerados."""
        response = auth_client.get(f'{BASE}/stats/infirmary/Sala Inexistente/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_current_year'] == 0
        assert response.data['total_today'] == 0
