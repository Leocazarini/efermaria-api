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
# Autenticação
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestPatientsAuth:
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
# Students — busca por nome
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestStudentSearch:
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
# Students — detalhe por ID
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestStudentDetail:
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
# Students — detalhe por matrícula
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestStudentByRegistry:
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
# Students — atualização de info clínica
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestStudentInfoUpdate:
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
# Employees — busca por nome
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestEmployeeSearch:
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


# ──────────────────────────────────────────────
# Employees — detalhe por ID e matrícula
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestEmployeeDetail:
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


# ──────────────────────────────────────────────
# Employees — atualização de info clínica
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestEmployeeInfoUpdate:
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
# Visitors — busca e detalhe
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestVisitorSearch:
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
    def test_get_by_id_returns_visitor_data(self, auth_client, visitor):
        """GET por ID retorna os dados do visitante."""
        response = auth_client.get(f'{BASE}/visitors/{visitor.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == visitor.email

    def test_get_by_invalid_id_returns_404(self, auth_client):
        """ID inexistente retorna 404."""
        response = auth_client.get(f'{BASE}/visitors/99999/')
        assert response.status_code == status.HTTP_404_NOT_FOUND
