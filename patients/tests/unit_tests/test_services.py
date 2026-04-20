"""
Testes unitários de patients/services.py.

Contratos documentados aqui:

  get_student_by_id(pk)
    → Retorna Student com select_related('info', 'class_group').
    → Levanta ObjectDoesNotExist se pk não encontrado.

  get_student_by_registry(registry)
    → Retorna Student pelo campo registry.
    → Levanta ObjectDoesNotExist se registry não encontrado.

  search_students_by_name(name)
    → Retorna lista de Students cujo nome contenha 'name' (icontains).
    → Levanta ValueError se name for vazio ou None.
    → Retorna [] quando não há correspondência.

  upsert_student_info(student_id, allergies, patient_notes)
    → Cria ou atualiza StudentInfo vinculado ao student_id.
    → Levanta ObjectDoesNotExist se student_id não existir.
    → Retorna a instância de StudentInfo atualizada.

  get_employee_by_id(pk) / get_employee_by_registry(registry)
    → Comportamento análogo ao de Student.

  search_employees_by_name(name) / upsert_employee_info(...)
    → Comportamento análogo ao de Student.

  get_visitor_by_id(pk)
    → Retorna Visitor pelo pk.
    → Levanta ObjectDoesNotExist se não encontrado.

  get_visitor_by_email(email)
    → Retorna Visitor pelo email, ou None se não encontrado (não levanta exceção).

  search_visitors_by_name(name)
    → Comportamento análogo a search_students_by_name.

  upsert_visitor(visitor_data)
    → Cria novo Visitor ou atualiza allergies/patient_notes do existente pelo email.
    → Levanta ValueError se visitor_data['email'] estiver vazio.
    → Chave de upsert: email (único por visitante).
"""
import pytest
from django.core.exceptions import ObjectDoesNotExist

from patients.models import (
    ClassGroup, Student, StudentInfo,
    Department, Employee, EmployeeInfo,
    Visitor,
)
from patients.services import (
    get_student_by_id,
    get_student_by_registry,
    search_students_by_name,
    upsert_student_info,
    get_employee_by_id,
    get_employee_by_registry,
    search_employees_by_name,
    upsert_employee_info,
    get_visitor_by_id,
    get_visitor_by_email,
    search_visitors_by_name,
    upsert_visitor,
)


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def class_group(db):
    return ClassGroup.objects.create(id='CG1', name='9A', segment='Fundamental', director='Dir. Silva')


@pytest.fixture
def student(db, class_group):
    return Student.objects.create(
        id='S1',
        name='Ana Lima',
        age=14,
        gender='Female',
        registry='STU001',
        class_group=class_group,
    )


@pytest.fixture
def student_info(db, student):
    return StudentInfo.objects.create(
        student=student,
        allergies='Penicillin',
        patient_notes='Asthmatic',
    )


@pytest.fixture
def department(db):
    return Department.objects.create(id='D1', name='TI', director='Dir. Costa')


@pytest.fixture
def employee(db, department):
    return Employee.objects.create(
        id='E1',
        name='Carlos Souza',
        age=35,
        gender='Male',
        registry='EMP001',
        department=department,
    )


@pytest.fixture
def employee_info(db, employee):
    return EmployeeInfo.objects.create(
        employee=employee,
        allergies='None',
        patient_notes='Hypertensive',
    )


@pytest.fixture
def visitor(db):
    return Visitor.objects.create(
        name='Maria Oliveira',
        age=40,
        gender='Female',
        email='maria@example.com',
        relationship='Mother',
        allergies='Pollen',
        patient_notes='',
    )


# ──────────────────────────────────────────────
# Student tests
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestGetStudentById:
    """get_student_by_id: busca por PK com join em info e class_group."""

    def test_returns_student_when_found(self, student):
        result = get_student_by_id(student.id)
        assert result.id == student.id
        assert result.name == 'Ana Lima'

    def test_raises_when_not_found(self, db):
        with pytest.raises(ObjectDoesNotExist):
            get_student_by_id('NONEXISTENT')


@pytest.mark.django_db
class TestGetStudentByRegistry:
    """get_student_by_registry: busca pelo campo registry (matrícula)."""

    def test_returns_student_when_found(self, student):
        result = get_student_by_registry('STU001')
        assert result.registry == 'STU001'

    def test_raises_when_not_found(self, db):
        with pytest.raises(ObjectDoesNotExist):
            get_student_by_registry('XXXXX')


@pytest.mark.django_db
class TestSearchStudentsByName:
    """search_students_by_name: filtro icontains por nome; rejeita nome vazio."""

    def test_returns_matching_students(self, student):
        results = search_students_by_name('Ana')
        assert len(results) == 1
        assert results[0].name == 'Ana Lima'

    def test_search_is_case_insensitive(self, student):
        results = search_students_by_name('ana')
        assert len(results) == 1

    def test_returns_empty_list_when_no_match(self, student):
        results = search_students_by_name('Zzzzzz')
        assert results == []

    def test_raises_when_name_is_empty(self, db):
        with pytest.raises(ValueError):
            search_students_by_name('')


@pytest.mark.django_db
class TestUpsertStudentInfo:
    """upsert_student_info: cria ou atualiza StudentInfo pelo student_id."""

    def test_creates_info_when_not_exists(self, student):
        info = upsert_student_info(student.id, 'Latex', 'Diabetic')
        assert info.student_id == student.id
        assert info.allergies == 'Latex'
        assert info.patient_notes == 'Diabetic'

    def test_updates_info_when_exists(self, student, student_info):
        updated = upsert_student_info(student.id, 'None', 'No issues')
        assert updated.allergies == 'None'
        assert updated.patient_notes == 'No issues'

    def test_raises_when_student_not_found(self, db):
        with pytest.raises(ObjectDoesNotExist):
            upsert_student_info('NONEXISTENT', 'None', '')


# ──────────────────────────────────────────────
# Employee tests
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestGetEmployeeById:
    """get_employee_by_id: busca por PK com join em info e department."""

    def test_returns_employee_when_found(self, employee):
        result = get_employee_by_id(employee.id)
        assert result.id == employee.id
        assert result.name == 'Carlos Souza'

    def test_raises_when_not_found(self, db):
        with pytest.raises(ObjectDoesNotExist):
            get_employee_by_id('NONEXISTENT')


@pytest.mark.django_db
class TestGetEmployeeByRegistry:
    """get_employee_by_registry: busca pelo campo registry (matrícula)."""

    def test_returns_employee_when_found(self, employee):
        result = get_employee_by_registry('EMP001')
        assert result.registry == 'EMP001'

    def test_raises_when_not_found(self, db):
        with pytest.raises(ObjectDoesNotExist):
            get_employee_by_registry('XXXXX')


@pytest.mark.django_db
class TestSearchEmployeesByName:
    """search_employees_by_name: filtro icontains por nome; rejeita nome vazio."""

    def test_returns_matching_employees(self, employee):
        results = search_employees_by_name('Carlos')
        assert len(results) == 1
        assert results[0].name == 'Carlos Souza'

    def test_search_is_case_insensitive(self, employee):
        results = search_employees_by_name('carlos')
        assert len(results) == 1

    def test_returns_empty_list_when_no_match(self, employee):
        results = search_employees_by_name('Zzzzzz')
        assert results == []

    def test_raises_when_name_is_empty(self, db):
        with pytest.raises(ValueError):
            search_employees_by_name('')


@pytest.mark.django_db
class TestUpsertEmployeeInfo:
    """upsert_employee_info: cria ou atualiza EmployeeInfo pelo employee_id."""

    def test_creates_info_when_not_exists(self, employee):
        info = upsert_employee_info(employee.id, 'Aspirin', 'Diabetic')
        assert info.employee_id == employee.id
        assert info.allergies == 'Aspirin'

    def test_updates_info_when_exists(self, employee, employee_info):
        updated = upsert_employee_info(employee.id, 'None', 'All clear')
        assert updated.allergies == 'None'
        assert updated.patient_notes == 'All clear'

    def test_raises_when_employee_not_found(self, db):
        with pytest.raises(ObjectDoesNotExist):
            upsert_employee_info('NONEXISTENT', 'None', '')


# ──────────────────────────────────────────────
# Visitor tests
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestGetVisitorById:
    """get_visitor_by_id: busca por PK; levanta ObjectDoesNotExist se ausente."""

    def test_returns_visitor_when_found(self, visitor):
        result = get_visitor_by_id(visitor.id)
        assert result.id == visitor.id
        assert result.name == 'Maria Oliveira'

    def test_raises_when_not_found(self, db):
        with pytest.raises(ObjectDoesNotExist):
            get_visitor_by_id(99999)


@pytest.mark.django_db
class TestGetVisitorByEmail:
    """get_visitor_by_email: busca por email; retorna None (não levanta exceção) se ausente."""

    def test_returns_visitor_when_found(self, visitor):
        result = get_visitor_by_email('maria@example.com')
        assert result.email == 'maria@example.com'

    def test_returns_none_when_not_found(self, db):
        result = get_visitor_by_email('notfound@example.com')
        assert result is None


@pytest.mark.django_db
class TestSearchVisitorsByName:
    """search_visitors_by_name: filtro icontains por nome; rejeita nome vazio."""

    def test_returns_matching_visitors(self, visitor):
        results = search_visitors_by_name('Maria')
        assert len(results) == 1

    def test_search_is_case_insensitive(self, visitor):
        results = search_visitors_by_name('maria')
        assert len(results) == 1

    def test_returns_empty_list_when_no_match(self, visitor):
        results = search_visitors_by_name('Zzzzzz')
        assert results == []

    def test_raises_when_name_is_empty(self, db):
        with pytest.raises(ValueError):
            search_visitors_by_name('')


@pytest.mark.django_db
class TestUpsertVisitor:
    """upsert_visitor: cria novo Visitor ou atualiza campos clínicos pelo email."""

    def test_creates_new_visitor_when_not_exists(self, db):
        data = {
            'name': 'Paulo Salave',
            'age': 45,
            'gender': 'Male',
            'email': 'paulo@example.com',
            'relationship': 'Father',
            'allergies': '',
            'patient_notes': '',
        }
        visitor = upsert_visitor(data)
        assert visitor.email == 'paulo@example.com'
        assert Visitor.objects.filter(email='paulo@example.com').exists()

    def test_returns_existing_visitor_when_email_matches(self, visitor):
        """Email já cadastrado reutiliza o mesmo registro; atualiza apenas campos clínicos."""
        data = {
            'name': 'Maria Oliveira',
            'age': 40,
            'gender': 'Female',
            'email': 'maria@example.com',
            'relationship': 'Mother',
            'allergies': 'Dust',
            'patient_notes': 'Updated note',
        }
        result = upsert_visitor(data)
        assert result.id == visitor.id
        result.refresh_from_db()
        assert result.allergies == 'Dust'
        assert result.patient_notes == 'Updated note'

    def test_raises_when_email_missing(self, db):
        with pytest.raises(ValueError):
            upsert_visitor({'name': 'No Email', 'age': 30, 'gender': 'Male', 'email': '', 'relationship': 'Other'})
