import pytest
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from patients.models import (
    ClassGroup, Student, StudentInfo,
    Department, Employee, EmployeeInfo,
    Visitor,
)
from appointments.models import StudentAppointment, EmployeeAppointment, VisitorAppointment
from appointments.services import (
    create_student_appointment,
    create_employee_appointment,
    create_visitor_appointment,
    get_appointments_by_patient,
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
def base_appointment_data():
    return {
        'infirmary': 'Enfermaria A',
        'nurse': 'Enf. Joana',
        'date': timezone.now(),
        'reason': 'Dor de cabeça',
        'treatment': 'Dipirona 500mg',
        'notes': '',
        'revaluation': False,
    }


# ──────────────────────────────────────────────
# Student appointment tests
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestCreateStudentAppointment:
    def test_creates_appointment_successfully(self, student, base_appointment_data):
        appt = create_student_appointment(
            student_id=student.id,
            current_class='9A',
            contact_parents=False,
            **base_appointment_data,
        )
        assert appt.pk is not None
        assert appt.student_id == student.id
        assert appt.reason == 'Dor de cabeça'
        assert StudentAppointment.objects.count() == 1

    def test_upserts_student_info_when_provided(self, student, base_appointment_data):
        create_student_appointment(
            student_id=student.id,
            current_class='9A',
            contact_parents=False,
            allergies='Aspirin',
            patient_notes='Asthmatic',
            **base_appointment_data,
        )
        student.refresh_from_db()
        assert student.info.allergies == 'Aspirin'
        assert student.info.patient_notes == 'Asthmatic'

    def test_raises_when_student_not_found(self, db, base_appointment_data):
        with pytest.raises(ObjectDoesNotExist):
            create_student_appointment(
                student_id='NONEXISTENT',
                current_class='9A',
                contact_parents=False,
                **base_appointment_data,
            )

    def test_raises_when_required_field_missing(self, student):
        with pytest.raises(TypeError):
            create_student_appointment(student_id=student.id)


# ──────────────────────────────────────────────
# Employee appointment tests
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestCreateEmployeeAppointment:
    def test_creates_appointment_successfully(self, employee, base_appointment_data):
        appt = create_employee_appointment(
            employee_id=employee.id,
            **base_appointment_data,
        )
        assert appt.pk is not None
        assert appt.employee_id == employee.id
        assert EmployeeAppointment.objects.count() == 1

    def test_upserts_employee_info_when_provided(self, employee, base_appointment_data):
        create_employee_appointment(
            employee_id=employee.id,
            allergies='Penicillin',
            patient_notes='Hypertensive',
            **base_appointment_data,
        )
        employee.refresh_from_db()
        assert employee.info.allergies == 'Penicillin'

    def test_raises_when_employee_not_found(self, db, base_appointment_data):
        with pytest.raises(ObjectDoesNotExist):
            create_employee_appointment(
                employee_id='NONEXISTENT',
                **base_appointment_data,
            )


# ──────────────────────────────────────────────
# Visitor appointment tests
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestCreateVisitorAppointment:
    def test_creates_appointment_for_existing_visitor(self, visitor, base_appointment_data):
        visitor_data = {
            'name': visitor.name,
            'age': visitor.age,
            'gender': visitor.gender,
            'email': visitor.email,
            'relationship': visitor.relationship,
            'allergies': '',
            'patient_notes': '',
        }
        appt = create_visitor_appointment(
            visitor_data=visitor_data,
            **base_appointment_data,
        )
        assert appt.pk is not None
        assert appt.visitor_id == visitor.id
        assert VisitorAppointment.objects.count() == 1

    def test_creates_new_visitor_and_appointment(self, db, base_appointment_data):
        visitor_data = {
            'name': 'Novo Visitante',
            'age': 30,
            'gender': 'Male',
            'email': 'novo@example.com',
            'relationship': 'Father',
            'allergies': '',
            'patient_notes': '',
        }
        appt = create_visitor_appointment(
            visitor_data=visitor_data,
            **base_appointment_data,
        )
        assert appt.pk is not None
        assert Visitor.objects.filter(email='novo@example.com').exists()

    def test_raises_when_email_missing(self, db, base_appointment_data):
        with pytest.raises(ValueError):
            create_visitor_appointment(
                visitor_data={'name': 'X', 'age': 20, 'gender': 'M', 'email': '', 'relationship': 'Other'},
                **base_appointment_data,
            )


# ──────────────────────────────────────────────
# Get appointments by patient tests
# ──────────────────────────────────────────────

@pytest.mark.django_db
class TestGetAppointmentsByPatient:
    def test_returns_student_appointments(self, student, base_appointment_data):
        StudentAppointment.objects.create(
            student=student,
            current_class='9A',
            contact_parents=False,
            **base_appointment_data,
        )
        results = get_appointments_by_patient(StudentAppointment, 'student_id', student.id)
        assert len(results) == 1
        assert results[0]['student_id'] == student.id

    def test_returns_empty_list_when_no_appointments(self, student):
        results = get_appointments_by_patient(StudentAppointment, 'student_id', student.id)
        assert results == []

    def test_returns_employee_appointments(self, employee, base_appointment_data):
        EmployeeAppointment.objects.create(employee=employee, **base_appointment_data)
        results = get_appointments_by_patient(EmployeeAppointment, 'employee_id', employee.id)
        assert len(results) == 1
