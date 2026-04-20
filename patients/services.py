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
    logger.debug(f"get_student_by_id: pk={pk}")
    return Student.objects.select_related('info', 'class_group').get(pk=pk)


def get_student_by_registry(registry):
    logger.debug(f"get_student_by_registry: registry={registry}")
    return Student.objects.select_related('info', 'class_group').get(registry=registry)


def search_students_by_name(name):
    if not name:
        raise ValueError("O parâmetro 'name' não pode ser vazio.")
    logger.debug(f"search_students_by_name: name={name}")
    return list(
        Student.objects.select_related('class_group')
        .filter(name__icontains=name)
    )


def upsert_student_info(student_id, allergies, patient_notes):
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
    logger.debug(f"get_employee_by_id: pk={pk}")
    return Employee.objects.select_related('info', 'department').get(pk=pk)


def get_employee_by_registry(registry):
    logger.debug(f"get_employee_by_registry: registry={registry}")
    return Employee.objects.select_related('info', 'department').get(registry=registry)


def search_employees_by_name(name):
    if not name:
        raise ValueError("O parâmetro 'name' não pode ser vazio.")
    logger.debug(f"search_employees_by_name: name={name}")
    return list(
        Employee.objects.select_related('department')
        .filter(name__icontains=name)
    )


def upsert_employee_info(employee_id, allergies, patient_notes):
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
    logger.debug(f"get_visitor_by_id: pk={pk}")
    return Visitor.objects.get(pk=pk)


def get_visitor_by_email(email):
    logger.debug(f"get_visitor_by_email: email={email}")
    try:
        return Visitor.objects.get(email=email)
    except Visitor.DoesNotExist:
        return None


def search_visitors_by_name(name):
    if not name:
        raise ValueError("O parâmetro 'name' não pode ser vazio.")
    logger.debug(f"search_visitors_by_name: name={name}")
    return list(Visitor.objects.filter(name__icontains=name))


def upsert_visitor(visitor_data):
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
