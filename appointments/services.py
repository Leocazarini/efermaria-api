import logging

from .models import StudentAppointment, EmployeeAppointment, VisitorAppointment
from patients.services import (
    get_student_by_id,
    get_employee_by_id,
    upsert_student_info,
    upsert_employee_info,
    upsert_visitor,
)

logger = logging.getLogger('appointments.services')


def create_student_appointment(
    student_id,
    infirmary,
    nurse,
    date,
    reason,
    treatment,
    current_class,
    contact_parents,
    notes=None,
    revaluation=False,
    allergies=None,
    patient_notes=None,
):
    """
    Create a StudentAppointment.
    If allergies or patient_notes are provided, upserts StudentInfo first.
    Raises ObjectDoesNotExist if the student does not exist.
    Returns the created StudentAppointment instance.
    """
    logger.debug(f"create_student_appointment: student_id={student_id}")
    student = get_student_by_id(student_id)

    if allergies is not None or patient_notes is not None:
        upsert_student_info(
            student_id,
            allergies or '',
            patient_notes or '',
        )

    return StudentAppointment.objects.create(
        student=student,
        infirmary=infirmary,
        nurse=nurse,
        current_class=current_class,
        date=date,
        reason=reason,
        treatment=treatment,
        notes=notes,
        revaluation=revaluation,
        contact_parents=contact_parents,
    )


def create_employee_appointment(
    employee_id,
    infirmary,
    nurse,
    date,
    reason,
    treatment,
    notes=None,
    revaluation=False,
    allergies=None,
    patient_notes=None,
):
    """
    Create an EmployeeAppointment.
    If allergies or patient_notes are provided, upserts EmployeeInfo first.
    Raises ObjectDoesNotExist if the employee does not exist.
    Returns the created EmployeeAppointment instance.
    """
    logger.debug(f"create_employee_appointment: employee_id={employee_id}")
    employee = get_employee_by_id(employee_id)

    if allergies is not None or patient_notes is not None:
        upsert_employee_info(
            employee_id,
            allergies or '',
            patient_notes or '',
        )

    return EmployeeAppointment.objects.create(
        employee=employee,
        infirmary=infirmary,
        nurse=nurse,
        date=date,
        reason=reason,
        treatment=treatment,
        notes=notes,
        revaluation=revaluation,
    )


def create_visitor_appointment(
    visitor_data,
    infirmary,
    nurse,
    date,
    reason,
    treatment,
    notes=None,
    revaluation=False,
):
    """
    Create a VisitorAppointment.
    Creates or updates the Visitor via upsert_visitor, then creates the appointment.
    Raises ValueError if visitor_data has no email.
    Returns the created VisitorAppointment instance.
    """
    logger.debug(f"create_visitor_appointment: email={visitor_data.get('email')}")
    visitor = upsert_visitor(visitor_data)

    return VisitorAppointment.objects.create(
        visitor=visitor,
        infirmary=infirmary,
        nurse=nurse,
        date=date,
        reason=reason,
        treatment=treatment,
        notes=notes,
        revaluation=revaluation,
    )


def get_pending_revaluations():
    """Return a unified list of all appointments where revaluation=True, across all patient types."""
    results = []

    for appt in StudentAppointment.objects.filter(revaluation=True).select_related('student').order_by('date'):
        results.append({
            'id': appt.id,
            'appointment_type': 'student',
            'patient_id': appt.student_id,
            'patient_name': appt.student.name,
            'infirmary': appt.infirmary,
            'nurse': appt.nurse,
            'date': appt.date.isoformat(),
            'reason': appt.reason,
            'notes': appt.notes,
        })

    for appt in EmployeeAppointment.objects.filter(revaluation=True).select_related('employee').order_by('date'):
        results.append({
            'id': appt.id,
            'appointment_type': 'employee',
            'patient_id': appt.employee_id,
            'patient_name': appt.employee.name,
            'infirmary': appt.infirmary,
            'nurse': appt.nurse,
            'date': appt.date.isoformat(),
            'reason': appt.reason,
            'notes': appt.notes,
        })

    for appt in VisitorAppointment.objects.filter(revaluation=True).select_related('visitor').order_by('date'):
        results.append({
            'id': appt.id,
            'appointment_type': 'visitor',
            'patient_id': appt.visitor_id,
            'patient_name': appt.visitor.name,
            'infirmary': appt.infirmary,
            'nurse': appt.nurse,
            'date': appt.date.isoformat(),
            'reason': appt.reason,
            'notes': appt.notes,
            'visitor_data': {
                'name': appt.visitor.name,
                'age': appt.visitor.age,
                'gender': appt.visitor.gender,
                'email': appt.visitor.email,
                'relationship': appt.visitor.relationship or '',
                'allergies': appt.visitor.allergies or '',
                'patient_notes': appt.visitor.patient_notes or '',
            },
        })

    results.sort(key=lambda x: x['date'])
    return results


def resolve_revaluation(appointment_type, appointment_id):
    """Set revaluation=False on the given appointment. Raises ValueError for invalid type."""
    model_map = {
        'student': StudentAppointment,
        'employee': EmployeeAppointment,
        'visitor': VisitorAppointment,
    }
    model = model_map.get(appointment_type)
    if model is None:
        raise ValueError(f'Tipo de atendimento inválido: {appointment_type}')

    appointment = model.objects.get(pk=appointment_id)
    appointment.revaluation = False
    appointment.save(update_fields=['revaluation', 'updated_at'])
    return appointment


def get_appointments_by_patient(appointment_model, identifier_field, patient_id):
    """
    Return a list of dicts for all appointments of a given patient.
    Uses a dynamic filter on identifier_field (e.g. 'student_id', 'employee_id').
    Returns [] when there are no records.
    """
    logger.debug(f"get_appointments_by_patient: model={appointment_model.__name__}, {identifier_field}={patient_id}")
    if patient_id is None:
        return []

    queryset = appointment_model.objects.filter(**{identifier_field: patient_id})
    return list(queryset.values())
