import pytest
from datetime import datetime, time
from django.utils import timezone

from patients.models import (
    ClassGroup, Student, Department, Employee, Visitor,
)
from appointments.models import StudentAppointment, EmployeeAppointment, VisitorAppointment
from reports.services import (
    get_all_appointments,
    get_nurse_appointments_current_year,
    get_total_appointments_current_year,
    get_total_appointments_today,
    get_total_appointments_infirmary_current_year,
    get_total_appointments_infirmary_today,
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


@pytest.fixture
def visitor_appointment(db, visitor):
    return VisitorAppointment.objects.create(
        visitor=visitor,
        infirmary='Enfermaria B',
        nurse='Enf. Pedro',
        date=timezone.now(),
        reason='Tontura',
        treatment='Repouso',
        revaluation=False,
    )


# ──────────────────────────────────────────────
# get_all_appointments tests
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestGetAllAppointments:
    def _date_range(self):
        today = timezone.now()
        start = timezone.make_aware(datetime.combine(today.date(), time.min))
        end = timezone.make_aware(datetime.combine(today.date(), time.max))
        return start, end

    def test_returns_student_appointment(self, student_appointment):
        start, end = self._date_range()
        results = get_all_appointments(start, end, ['Enfermaria A'], '')
        types = [r['patient_type'] for r in results]
        assert 'Estudante' in types

    def test_returns_employee_appointment(self, employee_appointment):
        start, end = self._date_range()
        results = get_all_appointments(start, end, ['Enfermaria A'], '')
        types = [r['patient_type'] for r in results]
        assert 'Funcionário' in types

    def test_returns_visitor_appointment(self, visitor_appointment):
        start, end = self._date_range()
        results = get_all_appointments(start, end, ['Enfermaria B'], '')
        types = [r['patient_type'] for r in results]
        assert 'Visitante' in types

    def test_filters_by_infirmary(self, student_appointment, visitor_appointment):
        start, end = self._date_range()
        results = get_all_appointments(start, end, ['Enfermaria B'], '')
        assert all(r['infirmary'] == 'Enfermaria B' for r in results)

    def test_filters_by_search_term(self, student_appointment, employee_appointment):
        start, end = self._date_range()
        results = get_all_appointments(start, end, ['Enfermaria A'], 'Dor')
        assert len(results) == 1
        assert results[0]['reason'] == 'Dor de cabeça'

    def test_returns_empty_when_no_match(self, db):
        start, end = self._date_range()
        results = get_all_appointments(start, end, ['Enfermaria A'], '')
        assert results == []

    def test_results_are_sorted_by_date_descending(self, student_appointment, employee_appointment):
        start, end = self._date_range()
        results = get_all_appointments(start, end, ['Enfermaria A'], '')
        dates = [r['date'] for r in results]
        assert dates == sorted(dates, reverse=True)


# ──────────────────────────────────────────────
# Statistics tests
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestGetNurseAppointmentsCurrentYear:
    def test_returns_nurse_counts(self, student_appointment):
        result = get_nurse_appointments_current_year()
        nurses = [entry['nurse'] for entry in result]
        assert 'Enf. Joana' in nurses

    def test_counts_correctly(self, student_appointment, employee_appointment):
        result = get_nurse_appointments_current_year()
        joana = next(e for e in result if e['nurse'] == 'Enf. Joana')
        assert joana['count'] == 2

    def test_returns_empty_when_no_appointments(self, db):
        result = get_nurse_appointments_current_year()
        assert result == []


@pytest.mark.django_db
class TestGetTotalAppointmentsCurrentYear:
    def test_counts_all_types(self, student_appointment, employee_appointment, visitor_appointment):
        total = get_total_appointments_current_year()
        assert total == 3

    def test_returns_zero_when_no_appointments(self, db):
        assert get_total_appointments_current_year() == 0


@pytest.mark.django_db
class TestGetTotalAppointmentsToday:
    def test_counts_todays_appointments(self, student_appointment):
        total = get_total_appointments_today()
        assert total >= 1

    def test_returns_zero_when_no_appointments(self, db):
        assert get_total_appointments_today() == 0


@pytest.mark.django_db
class TestGetTotalAppointmentsInfirmaryCurrentYear:
    def test_counts_for_specific_infirmary(self, student_appointment, employee_appointment):
        total = get_total_appointments_infirmary_current_year('Enfermaria A')
        assert total == 2

    def test_returns_zero_for_unknown_infirmary(self, student_appointment):
        total = get_total_appointments_infirmary_current_year('Sala Inexistente')
        assert total == 0

    def test_returns_zero_when_infirmary_is_none(self, db):
        assert get_total_appointments_infirmary_current_year(None) == 0


@pytest.mark.django_db
class TestGetTotalAppointmentsInfirmaryToday:
    def test_counts_for_specific_infirmary(self, student_appointment):
        total = get_total_appointments_infirmary_today('Enfermaria A')
        assert total == 1

    def test_returns_zero_for_unknown_infirmary(self, student_appointment):
        total = get_total_appointments_infirmary_today('Sala Inexistente')
        assert total == 0

    def test_returns_zero_when_infirmary_is_none(self, db):
        assert get_total_appointments_infirmary_today(None) == 0
