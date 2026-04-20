"""
Testes de integração — Jornadas de consulta de pacientes.

Jornadas de usuário cobertas:

  1. Busca de aluno por nome
     Intenção: enfermeira digita o nome do aluno no campo de busca para iniciar
     um atendimento ou consultar histórico.
     Fluxo técnico: GET /api/v1/patients/students/?name=<termo>
     → StudentSearchView → search_students_by_name() → SELECT icontains
     → Retorna lista serializada; sem parâmetro 'name' retorna 400.

  2. Consulta de aluno por ID ou matrícula
     Intenção: após selecionar o aluno na busca, sistema carrega seus dados completos.
     Fluxo técnico: GET /api/v1/patients/students/<id>/ ou /registry/<registry>/
     → StudentDetailView → get_student_by_id() / get_student_by_registry()
     → 404 se não encontrado.

  3. Atualização de informações clínicas do aluno
     Intenção: enfermeira registra alergias ou anotações clínicas durante o atendimento.
     Fluxo técnico: PATCH /api/v1/patients/students/<id>/info/
     → StudentInfoView → upsert_student_info() → UPDATE OR CREATE StudentInfo

  4-6. Jornadas análogas para funcionários (Employee) e visitantes (Visitor).

  Restrição comum: todos os endpoints exigem token JWT (IsAuthenticated).
  Sem token → 401; token inválido → 401.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

from patients.models import ClassGroup, Student, Department, Employee, Visitor

User = get_user_model()

BASE = '/api/v1/patients'


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


# ──────────────────────────────────────────────
# Jornada: proteção de rotas (sem token)
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestPatientsAuth:
    """Todos os endpoints de pacientes exigem JWT — sem token retorna 401."""

    def test_unauthenticated_student_search_returns_401(self, api_client):
        """Endpoints de pacientes requerem token JWT válido."""
        response = api_client.get(f'{BASE}/students/?name=ana')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_employee_search_returns_401(self, api_client):
        """Endpoints de funcionários requerem token JWT válido."""
        response = api_client.get(f'{BASE}/employees/?name=carlos')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_unauthenticated_visitor_search_returns_401(self, api_client):
        """Endpoints de visitantes requerem token JWT válido."""
        response = api_client.get(f'{BASE}/visitors/?name=maria')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ──────────────────────────────────────────────
# Jornada 1 — Busca de aluno por nome
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestStudentSearch:
    """
    Enfermeira pesquisa aluno pelo nome para iniciar atendimento.
    Fluxo: GET /students/?name= → search_students_by_name() → lista serializada.
    """

    def test_search_returns_matching_students(self, auth_client, student):
        """Busca por nome retorna lista de alunos com nome correspondente."""
        response = auth_client.get(f'{BASE}/students/?name=Ana')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Ana Lima'

    def test_search_is_case_insensitive(self, auth_client, student):
        """Busca por nome é case-insensitive."""
        response = auth_client.get(f'{BASE}/students/?name=ana')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_search_without_name_param_returns_400(self, auth_client):
        """Requisição sem parâmetro 'name' retorna 400."""
        response = auth_client.get(f'{BASE}/students/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_search_returns_empty_list_when_no_match(self, auth_client, student):
        """Busca sem correspondência retorna lista vazia e 200."""
        response = auth_client.get(f'{BASE}/students/?name=xyz_inexistente')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


# ──────────────────────────────────────────────
# Jornada 2a — Consulta de aluno por ID
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestStudentDetail:
    """
    Sistema carrega dados completos do aluno após seleção na busca.
    Fluxo: GET /students/<id>/ → get_student_by_id() → 404 se não encontrado.
    """

    def test_get_by_id_returns_student_data(self, auth_client, student):
        """GET por ID retorna os dados completos do aluno."""
        response = auth_client.get(f'{BASE}/students/{student.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == student.id
        assert response.data['name'] == student.name

    def test_get_by_invalid_id_returns_404(self, auth_client):
        """ID inexistente retorna 404."""
        response = auth_client.get(f'{BASE}/students/ID_INEXISTENTE/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ──────────────────────────────────────────────
# Jornada 2b — Consulta de aluno por matrícula
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestStudentByRegistry:
    """
    Sistema localiza aluno pela matrícula (código externo do ERP escolar).
    Fluxo: GET /students/registry/<registry>/ → get_student_by_registry().
    """

    def test_get_by_registry_returns_student_data(self, auth_client, student):
        """GET por matrícula retorna os dados do aluno correspondente."""
        response = auth_client.get(f'{BASE}/students/registry/{student.registry}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['registry'] == student.registry

    def test_get_by_invalid_registry_returns_404(self, auth_client):
        """Matrícula inexistente retorna 404."""
        response = auth_client.get(f'{BASE}/students/registry/INVALIDA/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ──────────────────────────────────────────────
# Jornada 3 — Atualização de informações clínicas do aluno
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestStudentInfoUpdate:
    """
    Enfermeira registra ou atualiza alergias e anotações clínicas durante o atendimento.
    Fluxo: PATCH /students/<id>/info/ → upsert_student_info() → UPDATE OR CREATE StudentInfo.
    """

    def test_patch_info_creates_and_returns_data(self, auth_client, student):
        """PATCH em /info/ cria ou atualiza informações clínicas do aluno."""
        payload = {'allergies': 'Dipirona', 'patient_notes': 'Histórico clínico'}
        response = auth_client.patch(
            f'{BASE}/students/{student.id}/info/', payload, format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['allergies'] == 'Dipirona'
        assert response.data['patient_notes'] == 'Histórico clínico'

    def test_patch_info_for_invalid_student_returns_404(self, auth_client):
        """PATCH para aluno inexistente retorna 404."""
        response = auth_client.patch(
            f'{BASE}/students/ID_INEXISTENTE/info/', {'allergies': 'x'}, format='json'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ──────────────────────────────────────────────
# Jornada 4 — Busca e consulta de funcionário
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestEmployeeSearch:
    """
    Enfermeira pesquisa funcionário pelo nome para registrar atendimento.
    Fluxo: GET /employees/?name= → search_employees_by_name().
    """

    def test_search_returns_matching_employees(self, auth_client, employee):
        """Busca por nome retorna lista de funcionários com nome correspondente."""
        response = auth_client.get(f'{BASE}/employees/?name=Carlos')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Carlos Souza'

    def test_search_without_name_param_returns_400(self, auth_client):
        """Requisição sem parâmetro 'name' retorna 400."""
        response = auth_client.get(f'{BASE}/employees/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_search_returns_empty_list_when_no_match(self, auth_client, employee):
        """Busca sem correspondência retorna lista vazia e 200."""
        response = auth_client.get(f'{BASE}/employees/?name=xyz_inexistente')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


@pytest.mark.django_db
class TestEmployeeDetail:
    """
    Sistema carrega dados completos do funcionário após seleção na busca.
    Fluxo: GET /employees/<id>/ ou /registry/<registry>/.
    """

    def test_get_by_id_returns_employee_data(self, auth_client, employee):
        """GET por ID retorna os dados do funcionário."""
        response = auth_client.get(f'{BASE}/employees/{employee.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == employee.id

    def test_get_by_invalid_id_returns_404(self, auth_client):
        """ID inexistente retorna 404."""
        response = auth_client.get(f'{BASE}/employees/ID_INEXISTENTE/')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_by_registry_returns_employee_data(self, auth_client, employee):
        """GET por matrícula retorna os dados do funcionário."""
        response = auth_client.get(f'{BASE}/employees/registry/{employee.registry}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['registry'] == employee.registry

    def test_get_by_invalid_registry_returns_404(self, auth_client):
        """Matrícula inexistente retorna 404."""
        response = auth_client.get(f'{BASE}/employees/registry/INVALIDA/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestEmployeeInfoUpdate:
    """
    Enfermeira registra informações clínicas do funcionário.
    Fluxo: PATCH /employees/<id>/info/ → upsert_employee_info().
    """

    def test_patch_info_creates_and_returns_data(self, auth_client, employee):
        """PATCH em /info/ cria ou atualiza informações clínicas do funcionário."""
        payload = {'allergies': 'Penicilina', 'patient_notes': 'Diabético'}
        response = auth_client.patch(
            f'{BASE}/employees/{employee.id}/info/', payload, format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['allergies'] == 'Penicilina'

    def test_patch_info_for_invalid_employee_returns_404(self, auth_client):
        """PATCH para funcionário inexistente retorna 404."""
        response = auth_client.patch(
            f'{BASE}/employees/ID_INEXISTENTE/info/', {'allergies': 'x'}, format='json'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


# ──────────────────────────────────────────────
# Jornada 5 — Busca e consulta de visitante
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestVisitorSearch:
    """
    Enfermeira pesquisa visitante pelo nome para consultar histórico.
    Fluxo: GET /visitors/?name= → search_visitors_by_name().
    """

    def test_search_returns_matching_visitors(self, auth_client, visitor):
        """Busca por nome retorna lista de visitantes com nome correspondente."""
        response = auth_client.get(f'{BASE}/visitors/?name=Maria')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'Maria Oliveira'

    def test_search_without_name_param_returns_400(self, auth_client):
        """Requisição sem parâmetro 'name' retorna 400."""
        response = auth_client.get(f'{BASE}/visitors/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_search_returns_empty_list_when_no_match(self, auth_client, visitor):
        """Busca sem correspondência retorna lista vazia e 200."""
        response = auth_client.get(f'{BASE}/visitors/?name=xyz_inexistente')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == []


@pytest.mark.django_db
class TestVisitorDetail:
    """
    Sistema carrega dados do visitante pelo ID.
    Fluxo: GET /visitors/<id>/ → get_visitor_by_id().
    """

    def test_get_by_id_returns_visitor_data(self, auth_client, visitor):
        """GET por ID retorna os dados do visitante."""
        response = auth_client.get(f'{BASE}/visitors/{visitor.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == visitor.email

    def test_get_by_invalid_id_returns_404(self, auth_client):
        """ID inexistente retorna 404."""
        response = auth_client.get(f'{BASE}/visitors/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
