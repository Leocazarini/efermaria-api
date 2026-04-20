"""
Testes de integração — Jornadas de registro de atendimentos.

Jornadas de usuário cobertas:

  1. Registro de atendimento de aluno
     Intenção: enfermeira registra o atendimento de um aluno que veio à enfermaria.
     Fluxo técnico: POST /api/v1/appointments/student/
     → StudentAppointmentCreateView → create_student_appointment()
     → Cria StudentAppointment; opcionalmente upserta StudentInfo se dados clínicos fornecidos.
     → 201 em sucesso; 404 se aluno não existe; 400 se campo obrigatório ausente.

  2. Consulta de histórico do aluno
     Intenção: enfermeira consulta todos os atendimentos anteriores de um aluno.
     Fluxo técnico: GET /api/v1/appointments/student/<student_id>/
     → get_appointments_by_patient(StudentAppointment, 'student_id', ...)
     → Lista vazia se o aluno não tiver histórico.

  3. Registro e consulta de atendimento de funcionário
     Intenção: análoga à do aluno, para colaboradores da escola.
     Fluxo técnico: POST /employee/ e GET /employee/<employee_id>/

  4. Registro e consulta de atendimento de visitante
     Intenção: visitante externo (pai, mãe, parceiro) é atendido na enfermaria.
     Fluxo técnico: POST /visitor/ → create_visitor_appointment()
     → upsert_visitor() cria ou reutiliza o Visitor pelo email antes do atendimento.
     → Dois POSTs com o mesmo email geram dois atendimentos mas um único Visitor.

  Restrição comum: todos os endpoints exigem token JWT (IsAuthenticated).
"""
import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from patients.models import ClassGroup, Student, Department, Employee, Visitor
from appointments.models import StudentAppointment, EmployeeAppointment, VisitorAppointment

User = get_user_model()

BASE = '/api/v1/appointments'


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
def visitor(db):
    return Visitor.objects.create(
        name='Maria Oliveira', age=40, gender='Female',
        email='maria@example.com', relationship='Mother',
    )


@pytest.fixture
def student_appointment_payload(student):
    return {
        'student_id': student.id,
        'infirmary': 'Enfermaria A',
        'nurse': 'Enf. Joana',
        'date': timezone.now().isoformat(),
        'reason': 'Dor de cabeça',
        'treatment': 'Dipirona',
        'current_class': '9A',
        'contact_parents': False,
        'revaluation': False,
    }


@pytest.fixture
def employee_appointment_payload(employee):
    return {
        'employee_id': employee.id,
        'infirmary': 'Enfermaria A',
        'nurse': 'Enf. Joana',
        'date': timezone.now().isoformat(),
        'reason': 'Pressão alta',
        'treatment': 'Repouso',
        'revaluation': False,
    }


@pytest.fixture
def visitor_appointment_payload():
    return {
        'visitor': {
            'name': 'João Pai',
            'age': 45,
            'gender': 'Male',
            'email': 'joao@example.com',
            'relationship': 'Father',
        },
        'infirmary': 'Enfermaria B',
        'nurse': 'Enf. Pedro',
        'date': timezone.now().isoformat(),
        'reason': 'Tontura',
        'treatment': 'Repouso',
        'revaluation': False,
    }


# ──────────────────────────────────────────────
# Proteção de rotas
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestAppointmentsAuth:
    """Todos os endpoints de atendimento exigem JWT — sem token retorna 401."""

    def test_unauthenticated_post_student_returns_401(self, api_client):
        """Criação de atendimento requer token JWT válido."""
        response = api_client.post(f'{BASE}/student/', {}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_get_student_appointments_returns_401(self, api_client):
        """Consulta de atendimentos requer token JWT válido."""
        response = api_client.get(f'{BASE}/student/S1/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ──────────────────────────────────────────────
# Jornada 1 — Registro de atendimento de aluno
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestCreateStudentAppointment:
    """
    Enfermeira registra atendimento de aluno na enfermaria.
    Fluxo: POST /student/ → create_student_appointment() → StudentAppointment criado.
    """

    def test_create_with_valid_payload_returns_201(self, auth_client, student_appointment_payload):
        """POST com payload válido cria atendimento e retorna 201."""
        response = auth_client.post(f'{BASE}/student/', student_appointment_payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['reason'] == 'Dor de cabeça'

    def test_create_with_nonexistent_student_returns_404(self, auth_client, student_appointment_payload):
        """POST com student_id inexistente retorna 404 — get_student_by_id() falha antes de criar."""
        student_appointment_payload['student_id'] = 'ID_INVALIDO'
        response = auth_client.post(f'{BASE}/student/', student_appointment_payload, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_missing_required_field_returns_400(self, auth_client, student_appointment_payload):
        """POST sem campo obrigatório retorna 400 — serializer valida antes de chamar o service."""
        del student_appointment_payload['reason']
        response = auth_client.post(f'{BASE}/student/', student_appointment_payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_with_clinical_info_upserts_student_info(self, auth_client, student, student_appointment_payload):
        """POST com allergies atualiza StudentInfo no mesmo request."""
        student_appointment_payload['allergies'] = 'Dipirona'
        student_appointment_payload['patient_notes'] = 'Observação'
        response = auth_client.post(f'{BASE}/student/', student_appointment_payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        student.refresh_from_db()
        assert student.info.allergies == 'Dipirona'


# ──────────────────────────────────────────────
# Jornada 2 — Consulta de histórico do aluno
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestGetStudentAppointments:
    """
    Enfermeira consulta todos os atendimentos anteriores de um aluno.
    Fluxo: GET /student/<student_id>/ → get_appointments_by_patient().
    """

    def test_get_appointments_returns_list(self, auth_client, student, student_appointment_payload):
        """GET retorna lista de atendimentos do aluno."""
        auth_client.post(f'{BASE}/student/', student_appointment_payload, format='json')
        response = auth_client.get(f'{BASE}/student/{student.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_get_appointments_returns_empty_list_for_no_history(self, auth_client, student):
        """GET retorna lista vazia para aluno sem atendimentos — não retorna 404."""
        response = auth_client.get(f'{BASE}/student/{student.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


# ──────────────────────────────────────────────
# Jornada 3 — Registro e consulta de atendimento de funcionário
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestCreateEmployeeAppointment:
    """
    Enfermeira registra atendimento de funcionário.
    Fluxo: POST /employee/ → create_employee_appointment().
    """

    def test_create_with_valid_payload_returns_201(self, auth_client, employee_appointment_payload):
        """POST com payload válido cria atendimento de funcionário e retorna 201."""
        response = auth_client.post(f'{BASE}/employee/', employee_appointment_payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['reason'] == 'Pressão alta'

    def test_create_with_nonexistent_employee_returns_404(self, auth_client, employee_appointment_payload):
        """POST com employee_id inexistente retorna 404."""
        employee_appointment_payload['employee_id'] = 'ID_INVALIDO'
        response = auth_client.post(f'{BASE}/employee/', employee_appointment_payload, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_missing_required_field_returns_400(self, auth_client, employee_appointment_payload):
        """POST sem campo obrigatório retorna 400."""
        del employee_appointment_payload['treatment']
        response = auth_client.post(f'{BASE}/employee/', employee_appointment_payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestGetEmployeeAppointments:
    """
    Enfermeira consulta histórico de atendimentos de um funcionário.
    Fluxo: GET /employee/<employee_id>/ → get_appointments_by_patient().
    """

    def test_get_appointments_returns_list(self, auth_client, employee, employee_appointment_payload):
        """GET retorna lista de atendimentos do funcionário."""
        auth_client.post(f'{BASE}/employee/', employee_appointment_payload, format='json')
        response = auth_client.get(f'{BASE}/employee/{employee.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_get_appointments_returns_empty_list_for_no_history(self, auth_client, employee):
        """GET retorna lista vazia para funcionário sem atendimentos."""
        response = auth_client.get(f'{BASE}/employee/{employee.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


# ──────────────────────────────────────────────
# Jornada 4 — Registro e consulta de atendimento de visitante
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestCreateVisitorAppointment:
    """
    Enfermeira registra atendimento de visitante externo (pai, mãe, parceiro).
    Fluxo: POST /visitor/ → create_visitor_appointment() → upsert_visitor() + VisitorAppointment.
    Email é a chave de upsert: visitante já cadastrado é reutilizado.
    """

    def test_create_with_valid_payload_returns_201(self, auth_client, visitor_appointment_payload):
        """POST com payload válido cria atendimento de visitante e retorna 201."""
        response = auth_client.post(f'{BASE}/visitor/', visitor_appointment_payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['reason'] == 'Tontura'

    def test_create_missing_visitor_email_returns_400(self, auth_client, visitor_appointment_payload):
        """POST com visitante sem e-mail retorna 400 — upsert_visitor() exige email."""
        del visitor_appointment_payload['visitor']['email']
        response = auth_client.post(f'{BASE}/visitor/', visitor_appointment_payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_missing_required_field_returns_400(self, auth_client, visitor_appointment_payload):
        """POST sem campo obrigatório retorna 400."""
        del visitor_appointment_payload['reason']
        response = auth_client.post(f'{BASE}/visitor/', visitor_appointment_payload, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_upserts_visitor_on_repeated_email(self, auth_client, visitor_appointment_payload):
        """Dois POSTs com o mesmo email geram dois atendimentos mas apenas um Visitor no banco."""
        auth_client.post(f'{BASE}/visitor/', visitor_appointment_payload, format='json')
        response = auth_client.post(f'{BASE}/visitor/', visitor_appointment_payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert Visitor.objects.filter(email='joao@example.com').count() == 1


@pytest.mark.django_db
class TestGetVisitorAppointments:
    """
    Enfermeira consulta histórico de atendimentos de um visitante.
    Fluxo: GET /visitor/<visitor_id>/ → get_appointments_by_patient().
    """

    def test_get_appointments_returns_list(self, auth_client, visitor, visitor_appointment_payload):
        """GET retorna lista de atendimentos do visitante."""
        auth_client.post(f'{BASE}/visitor/', visitor_appointment_payload, format='json')
        created_visitor = Visitor.objects.get(email='joao@example.com')
        response = auth_client.get(f'{BASE}/visitor/{created_visitor.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_get_appointments_returns_empty_list_for_no_history(self, auth_client, visitor):
        """GET retorna lista vazia para visitante sem atendimentos."""
        response = auth_client.get(f'{BASE}/visitor/{visitor.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []
