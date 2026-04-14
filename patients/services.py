import logging
from django.core.exceptions import ObjectDoesNotExist

from .models import (
    ClassGroup, Student, StudentInfo,
    Department, Employee, EmployeeInfo,
    Visitor,
)

logger = logging.getLogger('patients.services')


# ──────────────────────────────────────────────
# Student services
# ──────────────────────────────────────────────

def get_student_by_id(pk):
    """Return Student by primary key. Raises ObjectDoesNotExist if not found."""
    logger.debug(f"get_student_by_id: pk={pk}")
    return Student.objects.select_related('info', 'class_group').get(pk=pk)


def get_student_by_registry(registry):
    """Return Student by registry. Raises ObjectDoesNotExist if not found."""
    logger.debug(f"get_student_by_registry: registry={registry}")
    return Student.objects.select_related('info', 'class_group').get(registry=registry)


def search_students_by_name(name):
    """
    Return list of Students whose name contains *name* (case-insensitive).
    Raises ValueError if name is empty. Returns [] when no match.
    """
    if not name:
        raise ValueError("O parâmetro 'name' não pode ser vazio.")
    logger.debug(f"search_students_by_name: name={name}")
    return list(
        Student.objects.select_related('class_group')
        .filter(name__icontains=name)
    )


def upsert_student_info(student_id, allergies, patient_notes):
    """
    Create or update StudentInfo for the given student_id.
    Raises ObjectDoesNotExist if the student does not exist.
    Returns the StudentInfo instance.
    """
    logger.debug(f"upsert_student_info: student_id={student_id}")
    student = Student.objects.get(pk=student_id)
    info, _ = StudentInfo.objects.update_or_create(
        student=student,
        defaults={'allergies': allergies, 'patient_notes': patient_notes},
    )
    return info


# ──────────────────────────────────────────────
# Employee services
# ──────────────────────────────────────────────

def get_employee_by_id(pk):
    """Return Employee by primary key. Raises ObjectDoesNotExist if not found."""
    logger.debug(f"get_employee_by_id: pk={pk}")
    return Employee.objects.select_related('info', 'department').get(pk=pk)


def get_employee_by_registry(registry):
    """Return Employee by registry. Raises ObjectDoesNotExist if not found."""
    logger.debug(f"get_employee_by_registry: registry={registry}")
    return Employee.objects.select_related('info', 'department').get(registry=registry)


def search_employees_by_name(name):
    """
    Return list of Employees whose name contains *name* (case-insensitive).
    Raises ValueError if name is empty. Returns [] when no match.
    """
    if not name:
        raise ValueError("O parâmetro 'name' não pode ser vazio.")
    logger.debug(f"search_employees_by_name: name={name}")
    return list(
        Employee.objects.select_related('department')
        .filter(name__icontains=name)
    )


def upsert_employee_info(employee_id, allergies, patient_notes):
    """
    Create or update EmployeeInfo for the given employee_id.
    Raises ObjectDoesNotExist if the employee does not exist.
    Returns the EmployeeInfo instance.
    """
    logger.debug(f"upsert_employee_info: employee_id={employee_id}")
    employee = Employee.objects.get(pk=employee_id)
    info, _ = EmployeeInfo.objects.update_or_create(
        employee=employee,
        defaults={'allergies': allergies, 'patient_notes': patient_notes},
    )
    return info


# ──────────────────────────────────────────────
# Visitor services
# ──────────────────────────────────────────────

def get_visitor_by_id(pk):
    """Return Visitor by primary key. Raises ObjectDoesNotExist if not found."""
    logger.debug(f"get_visitor_by_id: pk={pk}")
    return Visitor.objects.get(pk=pk)


def get_visitor_by_email(email):
    """Return Visitor by email, or None if not found."""
    logger.debug(f"get_visitor_by_email: email={email}")
    try:
        return Visitor.objects.get(email=email)
    except Visitor.DoesNotExist:
        return None


def search_visitors_by_name(name):
    """
    Return list of Visitors whose name contains *name* (case-insensitive).
    Raises ValueError if name is empty. Returns [] when no match.
    """
    if not name:
        raise ValueError("O parâmetro 'name' não pode ser vazio.")
    logger.debug(f"search_visitors_by_name: name={name}")
    return list(Visitor.objects.filter(name__icontains=name))


def upsert_visitor(visitor_data):
    """
    Create a new Visitor or update an existing one matched by email.
    Raises ValueError if email is missing.
    Returns the Visitor instance.
    """
    email = visitor_data.get('email', '').strip()
    if not email:
        raise ValueError("O campo 'email' é obrigatório para visitantes.")

    logger.debug(f"upsert_visitor: email={email}")

    existing = get_visitor_by_email(email)
    if existing:
        existing.allergies = visitor_data.get('allergies', existing.allergies)
        existing.patient_notes = visitor_data.get('patient_notes', existing.patient_notes)
        existing.save(update_fields=['allergies', 'patient_notes'])
        return existing

    return Visitor.objects.create(
        name=visitor_data['name'],
        age=visitor_data['age'],
        gender=visitor_data['gender'],
        email=email,
        relationship=visitor_data.get('relationship', ''),
        allergies=visitor_data.get('allergies', ''),
        patient_notes=visitor_data.get('patient_notes', ''),
    )
