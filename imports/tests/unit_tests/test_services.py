"""
Testes unitários de imports/services.py.

Contratos documentados aqui:

  _calculate_age(birth_date_str)
    → Recebe string no formato DD/MM/YYYY; retorna inteiro com a idade calculada.
    → Retorna 0 para None, string vazia, espaços em branco ou formato inválido.

  _parse_csv(file_obj)
    → Lê arquivo CSV e retorna lista de dicts com os campos de cada linha de dados.
    → Retorna [] para arquivo com apenas cabeçalho.
    → Campos ausentes no CSV resultam em chaves ausentes ou com valor vazio no dict.
    → Decodifica UTF-8 com suporte a acentuação.

  _parse_xlsx(file_obj)
    → Lê arquivo XLSX e retorna lista de dicts (mesmo contrato que _parse_csv).
    → Células vazias são convertidas para string vazia (não None).
    → Retorna [] para planilha sem linhas de dados.

  _resolve_class_group(class_group_id)
    → Busca ClassGroup pelo id; se não encontrado (ou None/''), retorna ClassGroup padrão
      com id='NAO_INFORMADO', criado via get_or_create (nunca duplicado).

  _resolve_department(department_id)
    → Comportamento análogo a _resolve_class_group, para Department.

  _upsert_student(row, errors, row_number)
    → 'registry', 'name' e 'gender' são obrigatórios; ausência de qualquer um
      registra erro em `errors` com {'row': row_number, 'reason': ...} e retorna 'error'.
    → Se registry já existe: atualiza campos e retorna 'updated'.
    → Se registry não existe: cria novo Student (id = registry) e retorna 'created'.
    → 'birth_date' é opcional — quando presente, calcula e salva age.
    → Campos opcionais (email, father_name, mother_name, etc.) são gravados quando fornecidos.

  _upsert_employee(row, errors, row_number)
    → Contrato análogo ao de _upsert_student, para Employee.
    → Campo opcional 'position' é gravado quando fornecido.

  import_from_file(file_obj, entity_type, user)
    → Detecta formato pelo nome do arquivo (.csv ou .xlsx); ValueError para outros formatos.
    → ValueError para entity_type fora de {'students', 'employees'}.
    → Retorna ImportLog com: entity_type, total_rows, created_count, updated_count,
      error_count, errors (lista de dicts), filename, imported_by.
    → Linhas com erros não interrompem o processamento das demais.
    → CSV/XLSX vazio (só cabeçalho) retorna ImportLog com todas as contagens zeradas.
"""
import io
import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

from patients.models import ClassGroup, Department, Student, Employee

from imports.services import (
    _calculate_age,
    _parse_csv,
    _parse_xlsx,
    _resolve_class_group,
    _resolve_department,
    _upsert_student,
    _upsert_employee,
    import_from_file,
)


# ──────────────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────────────

def _make_xlsx_bytes(headers: list, rows: list) -> bytes:
    """Gera um .xlsx em memória com openpyxl para uso nos testes."""
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
# _calculate_age
# ──────────────────────────────────────────────────────────────────────────────

class TestCalculateAge:
    """_calculate_age: converte string DD/MM/YYYY em idade inteira; 0 para entradas inválidas."""
    def test_calculates_age_from_valid_date(self):
        """Calcula a idade a partir de uma data no formato DD/MM/YYYY."""
        age = _calculate_age('01/01/2000')
        assert age >= 24  # pelo menos 24 anos em 2024+

    def test_returns_0_for_empty_string(self):
        """Retorna 0 quando a string estiver vazia."""
        assert _calculate_age('') == 0

    def test_returns_0_for_none(self):
        """Retorna 0 quando o valor for None."""
        assert _calculate_age(None) == 0

    def test_returns_0_for_invalid_format(self):
        """Retorna 0 para uma string que não representa uma data válida."""
        assert _calculate_age('nao-e-uma-data') == 0

    def test_returns_0_for_whitespace(self):
        """Retorna 0 para string de espaços em branco."""
        assert _calculate_age('   ') == 0


# ──────────────────────────────────────────────────────────────────────────────
# _parse_csv
# ──────────────────────────────────────────────────────────────────────────────

class TestParseCSV:
    """_parse_csv: lê arquivo CSV e retorna lista de dicts; [] para arquivo sem linhas de dados."""
    def test_parses_all_columns(self):
        """Lê todas as colunas de um CSV simples."""
        csv_content = b"registry,name,gender\nSTU001,Ana Lima,F"
        file_obj = SimpleUploadedFile("students.csv", csv_content)
        rows = _parse_csv(file_obj)
        assert len(rows) == 1
        assert rows[0]['registry'] == 'STU001'
        assert rows[0]['name'] == 'Ana Lima'
        assert rows[0]['gender'] == 'F'

    def test_parses_multiple_rows(self):
        """Retorna múltiplas linhas corretamente."""
        csv_content = (
            b"registry,name,gender\n"
            b"STU001,Ana Lima,F\n"
            b"STU002,Bruno Souza,M\n"
        )
        file_obj = SimpleUploadedFile("students.csv", csv_content)
        rows = _parse_csv(file_obj)
        assert len(rows) == 2

    def test_returns_empty_list_for_header_only(self):
        """CSV com apenas o cabeçalho retorna lista vazia."""
        csv_content = b"registry,name,gender\n"
        file_obj = SimpleUploadedFile("students.csv", csv_content)
        rows = _parse_csv(file_obj)
        assert rows == []

    def test_handles_optional_columns_absent(self):
        """CSV sem colunas opcionais ainda gera dicts (com chaves ausentes)."""
        csv_content = b"registry,name,gender\nSTU001,Ana Lima,F"
        file_obj = SimpleUploadedFile("students.csv", csv_content)
        rows = _parse_csv(file_obj)
        assert 'birth_date' not in rows[0]
        assert rows[0].get('email', '') == ''

    def test_handles_utf8_with_accents(self):
        """CSV com acentos em UTF-8 é decodificado corretamente."""
        csv_content = "registry,name,gender\nSTU001,Bárbara Gonçalves,F".encode('utf-8')
        file_obj = SimpleUploadedFile("students.csv", csv_content)
        rows = _parse_csv(file_obj)
        assert rows[0]['name'] == 'Bárbara Gonçalves'


# ──────────────────────────────────────────────────────────────────────────────
# _parse_xlsx
# ──────────────────────────────────────────────────────────────────────────────

class TestParseXLSX:
    """_parse_xlsx: lê arquivo XLSX e retorna lista de dicts; células vazias viram string vazia."""
    def test_parses_all_columns(self):
        """Lê todas as colunas de um XLSX simples."""
        xlsx_bytes = _make_xlsx_bytes(
            ['registry', 'name', 'gender'],
            [['STU001', 'Ana Lima', 'F']],
        )
        file_obj = SimpleUploadedFile("students.xlsx", xlsx_bytes)
        rows = _parse_xlsx(file_obj)
        assert len(rows) == 1
        assert rows[0]['registry'] == 'STU001'
        assert rows[0]['name'] == 'Ana Lima'

    def test_parses_multiple_rows(self):
        """Retorna múltiplas linhas."""
        xlsx_bytes = _make_xlsx_bytes(
            ['registry', 'name', 'gender'],
            [
                ['STU001', 'Ana Lima', 'F'],
                ['STU002', 'Bruno Souza', 'M'],
            ],
        )
        file_obj = SimpleUploadedFile("students.xlsx", xlsx_bytes)
        rows = _parse_xlsx(file_obj)
        assert len(rows) == 2

    def test_returns_empty_list_for_header_only(self):
        """XLSX com apenas o cabeçalho retorna lista vazia."""
        xlsx_bytes = _make_xlsx_bytes(['registry', 'name', 'gender'], [])
        file_obj = SimpleUploadedFile("students.xlsx", xlsx_bytes)
        rows = _parse_xlsx(file_obj)
        assert rows == []

    def test_none_cells_become_empty_string(self):
        """Células vazias no XLSX são convertidas para string vazia."""
        xlsx_bytes = _make_xlsx_bytes(
            ['registry', 'name', 'gender', 'email'],
            [['STU001', 'Ana Lima', 'F', None]],
        )
        file_obj = SimpleUploadedFile("students.xlsx", xlsx_bytes)
        rows = _parse_xlsx(file_obj)
        assert rows[0]['email'] == ''


# ──────────────────────────────────────────────────────────────────────────────
# _resolve_class_group
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestResolveClassGroup:
    """_resolve_class_group: busca ClassGroup por id; retorna padrão 'NAO_INFORMADO' se ausente ou inválido."""
    def test_returns_existing_class_group(self):
        """Retorna o ClassGroup existente quando o id é encontrado."""
        cg = ClassGroup.objects.create(id='CG1', name='9A', segment='Fund', director='Dir')
        result = _resolve_class_group('CG1')
        assert result.id == 'CG1'

    def test_returns_default_when_id_not_found(self):
        """Retorna o ClassGroup padrão quando o id não existe no banco."""
        result = _resolve_class_group('INEXISTENTE')
        assert result.id == 'NAO_INFORMADO'
        assert result.name == 'Turma não informada'

    def test_returns_default_for_empty_string(self):
        """Retorna o ClassGroup padrão para string vazia."""
        result = _resolve_class_group('')
        assert result.id == 'NAO_INFORMADO'

    def test_returns_default_for_none(self):
        """Retorna o ClassGroup padrão para None."""
        result = _resolve_class_group(None)
        assert result.id == 'NAO_INFORMADO'

    def test_default_class_group_created_only_once(self):
        """get_or_create garante que o ClassGroup padrão não é duplicado."""
        _resolve_class_group('')
        _resolve_class_group('')
        assert ClassGroup.objects.filter(id='NAO_INFORMADO').count() == 1


# ──────────────────────────────────────────────────────────────────────────────
# _resolve_department
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestResolveDepartment:
    """_resolve_department: busca Department por id; retorna padrão 'NAO_INFORMADO' se ausente ou inválido."""
    def test_returns_existing_department(self):
        """Retorna o Department existente quando o id é encontrado."""
        dep = Department.objects.create(id='D1', name='TI', director='Dir')
        result = _resolve_department('D1')
        assert result.id == 'D1'

    def test_returns_default_when_id_not_found(self):
        """Retorna o Department padrão quando o id não existe."""
        result = _resolve_department('INEXISTENTE')
        assert result.id == 'NAO_INFORMADO'
        assert result.name == 'Departamento não informado'

    def test_returns_default_for_empty_string(self):
        """Retorna o Department padrão para string vazia."""
        result = _resolve_department('')
        assert result.id == 'NAO_INFORMADO'

    def test_returns_default_for_none(self):
        """Retorna o Department padrão para None."""
        result = _resolve_department(None)
        assert result.id == 'NAO_INFORMADO'

    def test_default_department_created_only_once(self):
        """get_or_create garante que o Department padrão não é duplicado."""
        _resolve_department('')
        _resolve_department('')
        assert Department.objects.filter(id='NAO_INFORMADO').count() == 1


# ──────────────────────────────────────────────────────────────────────────────
# _upsert_student
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestUpsertStudent:
    """_upsert_student: cria ou atualiza Student por registry; registra erros sem interromper o lote."""
    def test_creates_new_student_with_required_fields(self):
        """Cria um novo aluno quando a matrícula não existe no banco."""
        errors = []
        result = _upsert_student(
            {'registry': 'STU001', 'name': 'Ana Lima', 'gender': 'F'},
            errors, 1,
        )
        assert result == 'created'
        assert Student.objects.filter(registry='STU001').exists()
        assert len(errors) == 0

    def test_updates_existing_student(self):
        """Retorna 'updated' e altera os dados de um aluno já cadastrado."""
        ClassGroup.objects.get_or_create(
            id='NAO_INFORMADO',
            defaults={'name': 'Turma não informada', 'segment': 'Não informado', 'director': 'Não informado'},
        )
        Student.objects.create(id='STU001', registry='STU001', name='Ana Lima', age=14, gender='F')
        errors = []
        result = _upsert_student(
            {'registry': 'STU001', 'name': 'Ana Lima Atualizada', 'gender': 'F'},
            errors, 1,
        )
        assert result == 'updated'
        student = Student.objects.get(registry='STU001')
        assert student.name == 'Ana Lima Atualizada'

    def test_returns_error_when_registry_missing(self):
        """Retorna 'error' e registra a causa quando 'registry' está ausente."""
        errors = []
        result = _upsert_student({'name': 'Ana Lima', 'gender': 'F'}, errors, 2)
        assert result == 'error'
        assert errors[0]['row'] == 2
        assert 'registry' in errors[0]['reason'].lower()

    def test_returns_error_when_name_missing(self):
        """Retorna 'error' quando 'name' está ausente."""
        errors = []
        result = _upsert_student({'registry': 'STU001', 'gender': 'F'}, errors, 3)
        assert result == 'error'
        assert 'name' in errors[0]['reason'].lower()

    def test_returns_error_when_gender_missing(self):
        """Retorna 'error' quando 'gender' está ausente."""
        errors = []
        result = _upsert_student({'registry': 'STU001', 'name': 'Ana Lima'}, errors, 4)
        assert result == 'error'
        assert 'gender' in errors[0]['reason'].lower()

    def test_student_id_set_to_registry_on_creation(self):
        """O id do Student recém-criado deve ser igual ao registry."""
        errors = []
        _upsert_student({'registry': 'STU999', 'name': 'Novo Aluno', 'gender': 'M'}, errors, 1)
        student = Student.objects.get(registry='STU999')
        assert student.id == 'STU999'

    def test_birth_date_parsed_and_age_calculated(self):
        """Quando birth_date é fornecido, age é calculado automaticamente."""
        errors = []
        _upsert_student(
            {'registry': 'STU002', 'name': 'Carlos', 'gender': 'M', 'birth_date': '15/06/2005'},
            errors, 1,
        )
        student = Student.objects.get(registry='STU002')
        assert student.age >= 18

    def test_optional_fields_stored(self):
        """Campos opcionais são gravados quando fornecidos."""
        errors = []
        _upsert_student(
            {
                'registry': 'STU003',
                'name': 'Maria',
                'gender': 'F',
                'email': 'maria@escola.com',
                'father_name': 'José',
                'mother_name': 'Clara',
            },
            errors, 1,
        )
        student = Student.objects.get(registry='STU003')
        assert student.email == 'maria@escola.com'
        assert student.father_name == 'José'
        assert student.mother_name == 'Clara'


# ──────────────────────────────────────────────────────────────────────────────
# _upsert_employee
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestUpsertEmployee:
    """_upsert_employee: cria ou atualiza Employee por registry; contrato análogo ao de _upsert_student."""
    def test_creates_new_employee_with_required_fields(self):
        """Cria um novo funcionário quando a matrícula não existe."""
        errors = []
        result = _upsert_employee(
            {'registry': 'EMP001', 'name': 'Carlos Souza', 'gender': 'M'},
            errors, 1,
        )
        assert result == 'created'
        assert Employee.objects.filter(registry='EMP001').exists()
        assert len(errors) == 0

    def test_updates_existing_employee(self):
        """Retorna 'updated' e altera os dados de um funcionário já cadastrado."""
        Department.objects.get_or_create(
            id='NAO_INFORMADO',
            defaults={'name': 'Departamento não informado', 'director': 'Não informado'},
        )
        Employee.objects.create(id='EMP001', registry='EMP001', name='Carlos Souza', age=35, gender='M')
        errors = []
        result = _upsert_employee(
            {'registry': 'EMP001', 'name': 'Carlos Souza Atualizado', 'gender': 'M'},
            errors, 1,
        )
        assert result == 'updated'
        emp = Employee.objects.get(registry='EMP001')
        assert emp.name == 'Carlos Souza Atualizado'

    def test_returns_error_when_registry_missing(self):
        """Retorna 'error' quando 'registry' está ausente."""
        errors = []
        result = _upsert_employee({'name': 'Carlos', 'gender': 'M'}, errors, 5)
        assert result == 'error'
        assert errors[0]['row'] == 5
        assert 'registry' in errors[0]['reason'].lower()

    def test_returns_error_when_name_missing(self):
        """Retorna 'error' quando 'name' está ausente."""
        errors = []
        result = _upsert_employee({'registry': 'EMP001', 'gender': 'M'}, errors, 6)
        assert result == 'error'
        assert 'name' in errors[0]['reason'].lower()

    def test_returns_error_when_gender_missing(self):
        """Retorna 'error' quando 'gender' está ausente."""
        errors = []
        result = _upsert_employee({'registry': 'EMP001', 'name': 'Carlos'}, errors, 7)
        assert result == 'error'
        assert 'gender' in errors[0]['reason'].lower()

    def test_employee_id_set_to_registry_on_creation(self):
        """O id do Employee recém-criado deve ser igual ao registry."""
        errors = []
        _upsert_employee({'registry': 'EMP999', 'name': 'Novo Func', 'gender': 'M'}, errors, 1)
        emp = Employee.objects.get(registry='EMP999')
        assert emp.id == 'EMP999'

    def test_position_stored_when_provided(self):
        """O campo 'position' é gravado quando fornecido."""
        errors = []
        _upsert_employee(
            {'registry': 'EMP002', 'name': 'Ana', 'gender': 'F', 'position': 'Professora'},
            errors, 1,
        )
        emp = Employee.objects.get(registry='EMP002')
        assert emp.position == 'Professora'


# ──────────────────────────────────────────────────────────────────────────────
# import_from_file — função principal
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.django_db
class TestImportFromFile:
    """import_from_file: orquestra parse + upsert e persiste o resultado em ImportLog."""
    @pytest.fixture
    def admin_user(self, db):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return User.objects.create_user(
            username='admin_svc', password='Pass1234!', is_staff=True
        )

    def test_imports_students_from_csv_and_returns_log(self, admin_user):
        """Importa alunos de um CSV válido e retorna ImportLog com contagens."""
        csv_content = (
            b"registry,name,gender\n"
            b"STU001,Ana Lima,F\n"
            b"STU002,Bruno Souza,M\n"
        )
        file_obj = SimpleUploadedFile("students.csv", csv_content)
        from imports.models import ImportLog
        log = import_from_file(file_obj, 'students', admin_user)

        assert isinstance(log, ImportLog)
        assert log.entity_type == 'students'
        assert log.total_rows == 2
        assert log.created_count == 2
        assert log.updated_count == 0
        assert log.error_count == 0
        assert log.errors == []
        assert log.imported_by == admin_user

    def test_imports_employees_from_csv_and_returns_log(self, admin_user):
        """Importa funcionários de um CSV válido e retorna ImportLog."""
        csv_content = (
            b"registry,name,gender\n"
            b"EMP001,Carlos Souza,M\n"
        )
        file_obj = SimpleUploadedFile("employees.csv", csv_content)
        log = import_from_file(file_obj, 'employees', admin_user)

        assert log.entity_type == 'employees'
        assert log.created_count == 1

    def test_upsert_updates_existing_records(self, admin_user):
        """Registros com registry já existente são atualizados (not criados)."""
        ClassGroup.objects.get_or_create(
            id='NAO_INFORMADO',
            defaults={'name': 'Turma não informada', 'segment': 'Não informado', 'director': 'Não informado'},
        )
        Student.objects.create(id='STU001', registry='STU001', name='Ana Lima', age=14, gender='F')

        csv_content = b"registry,name,gender\nSTU001,Ana Lima Nova,F"
        file_obj = SimpleUploadedFile("students.csv", csv_content)
        log = import_from_file(file_obj, 'students', admin_user)

        assert log.created_count == 0
        assert log.updated_count == 1

    def test_rows_with_missing_required_fields_counted_as_errors(self, admin_user):
        """Linhas com campos obrigatórios ausentes são contadas em error_count."""
        csv_content = (
            b"registry,name,gender\n"
            b"STU001,Ana Lima,F\n"
            b",Sem Matricula,M\n"      # registry ausente → erro
            b"STU003,,M\n"             # name ausente → erro
        )
        file_obj = SimpleUploadedFile("students.csv", csv_content)
        log = import_from_file(file_obj, 'students', admin_user)

        assert log.total_rows == 3
        assert log.created_count == 1
        assert log.error_count == 2
        assert len(log.errors) == 2
        assert log.errors[0]['row'] == 2
        assert log.errors[1]['row'] == 3

    def test_errors_list_contains_row_and_reason(self, admin_user):
        """Cada entrada em errors contém 'row' e 'reason'."""
        csv_content = b"registry,name,gender\n,Sem Matricula,M"
        file_obj = SimpleUploadedFile("students.csv", csv_content)
        log = import_from_file(file_obj, 'students', admin_user)

        assert 'row' in log.errors[0]
        assert 'reason' in log.errors[0]

    def test_import_log_stores_filename(self, admin_user):
        """O ImportLog registra o nome do arquivo importado."""
        csv_content = b"registry,name,gender\nSTU001,Ana Lima,F"
        file_obj = SimpleUploadedFile("alunos_2024.csv", csv_content)
        log = import_from_file(file_obj, 'students', admin_user)
        assert log.filename == 'alunos_2024.csv'

    def test_imports_students_from_xlsx(self, admin_user):
        """Importa alunos corretamente de um arquivo .xlsx."""
        xlsx_bytes = _make_xlsx_bytes(
            ['registry', 'name', 'gender'],
            [['STU001', 'Ana Lima', 'F'], ['STU002', 'Bruno Souza', 'M']],
        )
        file_obj = SimpleUploadedFile("students.xlsx", xlsx_bytes)
        log = import_from_file(file_obj, 'students', admin_user)
        assert log.created_count == 2

    def test_raises_value_error_for_unsupported_entity_type(self, admin_user):
        """Lança ValueError para entity_type inválido."""
        csv_content = b"registry,name,gender\nSTU001,Ana,F"
        file_obj = SimpleUploadedFile("students.csv", csv_content)
        with pytest.raises(ValueError, match='entity_type'):
            import_from_file(file_obj, 'visitantes', admin_user)

    def test_raises_value_error_for_unsupported_file_extension(self, admin_user):
        """Lança ValueError para extensão de arquivo não suportada."""
        file_obj = SimpleUploadedFile("students.txt", b"some content")
        with pytest.raises(ValueError, match='(?i)formato'):
            import_from_file(file_obj, 'students', admin_user)

    def test_empty_csv_creates_log_with_zero_counts(self, admin_user):
        """CSV sem dados (só cabeçalho) cria ImportLog com contagens zeradas."""
        csv_content = b"registry,name,gender\n"
        file_obj = SimpleUploadedFile("students.csv", csv_content)
        log = import_from_file(file_obj, 'students', admin_user)
        assert log.total_rows == 0
        assert log.created_count == 0
        assert log.updated_count == 0
        assert log.error_count == 0
