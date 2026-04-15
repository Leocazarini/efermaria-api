"""
Testes de integração para os endpoints do módulo imports/.

Cobre os dois endpoints:
  POST /api/v1/imports/file/  — importação via arquivo (CSV/XLSX)
  POST /api/v1/imports/sync/  — stub de sincronização externa (501)
"""
import io
import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from patients.models import Student, Employee

User = get_user_model()

BASE = '/api/v1/imports'


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _make_xlsx_bytes(headers: list, rows: list) -> bytes:
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


# ──────────────────────────────────────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def auth_client(db):
    """APIClient autenticado como usuário comum (não staff)."""
    user = User.objects.create_user(username='user_comum', password='Pass1234!')
    client = APIClient()
    response = client.post(
        '/api/auth/login/',
        {'username': 'user_comum', 'password': 'Pass1234!'},
        format='json',
    )
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client


@pytest.fixture
def admin_client(db):
    """APIClient autenticado como administrador (is_staff=True)."""
    user = User.objects.create_user(
        username='admin_user', password='Pass1234!', is_staff=True
    )
    client = APIClient()
    response = client.post(
        '/api/auth/login/',
        {'username': 'admin_user', 'password': 'Pass1234!'},
        format='json',
    )
    token = response.data['access']
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
    return client


# ──────────────────────────────────────────────────────────────────────────────
# Autenticação e permissão — /file/
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFileImportAuth:
    def test_unauthenticated_returns_401(self, api_client):
        """Requisição sem token retorna 401."""
        csv_file = SimpleUploadedFile("s.csv", b"registry,name,gender\n")
        response = api_client.post(
            f'{BASE}/file/',
            {'entity_type': 'students', 'file': csv_file},
            format='multipart',
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_admin_user_returns_403(self, auth_client):
        """Usuário autenticado sem is_staff recebe 403."""
        csv_file = SimpleUploadedFile("s.csv", b"registry,name,gender\n")
        response = auth_client.post(
            f'{BASE}/file/',
            {'entity_type': 'students', 'file': csv_file},
            format='multipart',
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


# ──────────────────────────────────────────────────────────────────────────────
# Importação de alunos via CSV
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFileImportStudentsCSV:
    def test_valid_csv_returns_200_and_import_summary(self, admin_client):
        """CSV válido retorna 200 com o resumo da importação."""
        csv_content = (
            b"registry,name,gender\n"
            b"STU001,Ana Lima,F\n"
            b"STU002,Bruno Souza,M\n"
        )
        csv_file = SimpleUploadedFile("students.csv", csv_content, content_type="text/csv")
        response = admin_client.post(
            f'{BASE}/file/',
            {'entity_type': 'students', 'file': csv_file},
            format='multipart',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['entity_type'] == 'students'
        assert response.data['total_rows'] == 2
        assert response.data['created'] == 2
        assert response.data['updated'] == 0
        assert response.data['errors'] == []
        assert 'import_id' in response.data

    def test_students_are_persisted_in_database(self, admin_client):
        """Após a importação, os alunos estão gravados no banco."""
        csv_content = b"registry,name,gender\nSTU001,Ana Lima,F"
        csv_file = SimpleUploadedFile("students.csv", csv_content)
        admin_client.post(
            f'{BASE}/file/',
            {'entity_type': 'students', 'file': csv_file},
            format='multipart',
        )
        assert Student.objects.filter(registry='STU001').exists()

    def test_reimport_updates_existing_students(self, admin_client):
        """Segunda importação do mesmo registry atualiza o registro."""
        from patients.models import ClassGroup
        ClassGroup.objects.get_or_create(
            id='NAO_INFORMADO',
            defaults={'name': 'Turma não informada', 'segment': 'Não informado', 'director': 'Não informado'},
        )
        Student.objects.create(id='STU001', registry='STU001', name='Ana Lima', age=14, gender='F')

        csv_content = b"registry,name,gender\nSTU001,Ana Lima Atualizada,F"
        csv_file = SimpleUploadedFile("students.csv", csv_content)
        response = admin_client.post(
            f'{BASE}/file/',
            {'entity_type': 'students', 'file': csv_file},
            format='multipart',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['updated'] == 1
        assert response.data['created'] == 0

    def test_csv_with_errors_returns_200_with_error_list(self, admin_client):
        """CSV com linhas inválidas retorna 200 e lista de erros."""
        csv_content = (
            b"registry,name,gender\n"
            b"STU001,Ana Lima,F\n"
            b",Sem Matricula,M\n"
        )
        csv_file = SimpleUploadedFile("students.csv", csv_content)
        response = admin_client.post(
            f'{BASE}/file/',
            {'entity_type': 'students', 'file': csv_file},
            format='multipart',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['created'] == 1
        assert len(response.data['errors']) == 1
        assert response.data['errors'][0]['row'] == 2

    def test_missing_file_field_returns_400(self, admin_client):
        """Requisição sem o campo 'file' retorna 400."""
        response = admin_client.post(
            f'{BASE}/file/',
            {'entity_type': 'students'},
            format='multipart',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_entity_type_returns_400(self, admin_client):
        """Requisição sem o campo 'entity_type' retorna 400."""
        csv_file = SimpleUploadedFile("students.csv", b"registry,name,gender\n")
        response = admin_client.post(
            f'{BASE}/file/',
            {'file': csv_file},
            format='multipart',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_entity_type_returns_400(self, admin_client):
        """entity_type com valor inválido retorna 400."""
        csv_file = SimpleUploadedFile("students.csv", b"registry,name,gender\n")
        response = admin_client.post(
            f'{BASE}/file/',
            {'entity_type': 'visitantes', 'file': csv_file},
            format='multipart',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unsupported_file_extension_returns_400(self, admin_client):
        """Arquivo com extensão inválida (.txt, .json, etc.) retorna 400."""
        txt_file = SimpleUploadedFile("students.txt", b"registry,name,gender\n")
        response = admin_client.post(
            f'{BASE}/file/',
            {'entity_type': 'students', 'file': txt_file},
            format='multipart',
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_empty_csv_returns_200_with_zero_counts(self, admin_client):
        """CSV vazio (apenas cabeçalho) retorna 200 com contagens zeradas."""
        csv_file = SimpleUploadedFile("students.csv", b"registry,name,gender\n")
        response = admin_client.post(
            f'{BASE}/file/',
            {'entity_type': 'students', 'file': csv_file},
            format='multipart',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['total_rows'] == 0
        assert response.data['created'] == 0


# ──────────────────────────────────────────────────────────────────────────────
# Importação de alunos via XLSX
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFileImportStudentsXLSX:
    def test_valid_xlsx_returns_200(self, admin_client):
        """XLSX válido é aceito e retorna 200 com o resumo."""
        xlsx_bytes = _make_xlsx_bytes(
            ['registry', 'name', 'gender'],
            [['STU001', 'Ana Lima', 'F'], ['STU002', 'Bruno Souza', 'M']],
        )
        xlsx_file = SimpleUploadedFile(
            "students.xlsx", xlsx_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response = admin_client.post(
            f'{BASE}/file/',
            {'entity_type': 'students', 'file': xlsx_file},
            format='multipart',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['created'] == 2

    def test_xlsx_students_persisted(self, admin_client):
        """Alunos importados via XLSX são gravados no banco."""
        xlsx_bytes = _make_xlsx_bytes(
            ['registry', 'name', 'gender'],
            [['STU010', 'Lucia Mendes', 'F']],
        )
        xlsx_file = SimpleUploadedFile("students.xlsx", xlsx_bytes)
        admin_client.post(
            f'{BASE}/file/',
            {'entity_type': 'students', 'file': xlsx_file},
            format='multipart',
        )
        assert Student.objects.filter(registry='STU010').exists()


# ──────────────────────────────────────────────────────────────────────────────
# Importação de funcionários
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestFileImportEmployees:
    def test_valid_csv_creates_employees(self, admin_client):
        """CSV de funcionários válido cria registros no banco."""
        csv_content = (
            b"registry,name,gender,position\n"
            b"EMP001,Carlos Souza,M,Professor\n"
            b"EMP002,Lucia Santos,F,Coordenadora\n"
        )
        csv_file = SimpleUploadedFile("employees.csv", csv_content)
        response = admin_client.post(
            f'{BASE}/file/',
            {'entity_type': 'employees', 'file': csv_file},
            format='multipart',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['entity_type'] == 'employees'
        assert response.data['created'] == 2

    def test_employees_are_persisted_in_database(self, admin_client):
        """Após a importação, os funcionários estão gravados no banco."""
        csv_content = b"registry,name,gender\nEMP001,Carlos Souza,M"
        csv_file = SimpleUploadedFile("employees.csv", csv_content)
        admin_client.post(
            f'{BASE}/file/',
            {'entity_type': 'employees', 'file': csv_file},
            format='multipart',
        )
        assert Employee.objects.filter(registry='EMP001').exists()

    def test_xlsx_employees_import(self, admin_client):
        """XLSX de funcionários é importado corretamente."""
        xlsx_bytes = _make_xlsx_bytes(
            ['registry', 'name', 'gender'],
            [['EMP010', 'Fernanda Lima', 'F']],
        )
        xlsx_file = SimpleUploadedFile("employees.xlsx", xlsx_bytes)
        response = admin_client.post(
            f'{BASE}/file/',
            {'entity_type': 'employees', 'file': xlsx_file},
            format='multipart',
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data['created'] == 1


# ──────────────────────────────────────────────────────────────────────────────
# Sincronização externa — /sync/
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestExternalSync:
    def test_admin_post_returns_501(self, admin_client):
        """POST em /sync/ retorna 501 Not Implemented."""
        response = admin_client.post(
            f'{BASE}/sync/',
            {'source': 'totvs_rm', 'entity_type': 'students', 'records': []},
            format='json',
        )
        assert response.status_code == status.HTTP_501_NOT_IMPLEMENTED

    def test_response_contains_detail_message(self, admin_client):
        """Resposta 501 contém campo 'detail' com mensagem."""
        response = admin_client.post(f'{BASE}/sync/', {}, format='json')
        assert 'detail' in response.data

    def test_unauthenticated_returns_401(self, api_client):
        """Requisição sem token em /sync/ retorna 401."""
        response = api_client.post(f'{BASE}/sync/', {}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_admin_returns_403(self, auth_client):
        """Usuário sem is_staff recebe 403 em /sync/."""
        response = auth_client.post(f'{BASE}/sync/', {}, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN
