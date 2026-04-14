import logging
from collections import defaultdict
from datetime import datetime

from django.db.models import Q
from django.utils import timezone

from appointments.models import StudentAppointment, EmployeeAppointment, VisitorAppointment

logger = logging.getLogger('reports.services')


def _get_student_appointments(date_begin, date_end, infirmaries, search_term):
    filters = Q(date__range=[date_begin, date_end], infirmary__in=infirmaries)

    if search_term:
        search_filters = (
            Q(student__name__icontains=search_term)
            | Q(current_class__icontains=search_term)
            | Q(student__class_group__name__icontains=search_term)
            | Q(reason__icontains=search_term)
            | Q(treatment__icontains=search_term)
            | Q(notes__icontains=search_term)
            | Q(infirmary__icontains=search_term)
            | Q(nurse__icontains=search_term)
        )
        try:
            search_date = datetime.strptime(search_term, '%d/%m/%Y').date()
            search_filters |= Q(date__date=search_date)
        except ValueError:
            pass
        filters &= search_filters

    return StudentAppointment.objects.filter(filters).select_related('student__class_group')


def _get_employee_appointments(date_begin, date_end, infirmaries, search_term):
    filters = Q(date__range=[date_begin, date_end], infirmary__in=infirmaries)

    if search_term:
        search_filters = (
            Q(employee__name__icontains=search_term)
            | Q(employee__department__name__icontains=search_term)
            | Q(reason__icontains=search_term)
            | Q(treatment__icontains=search_term)
            | Q(notes__icontains=search_term)
            | Q(infirmary__icontains=search_term)
            | Q(nurse__icontains=search_term)
        )
        try:
            search_date = datetime.strptime(search_term, '%d/%m/%Y').date()
            search_filters |= Q(date__date=search_date)
        except ValueError:
            pass
        filters &= search_filters

    return EmployeeAppointment.objects.filter(filters).select_related('employee__department')


def _get_visitor_appointments(date_begin, date_end, infirmaries, search_term):
    filters = Q(date__range=[date_begin, date_end], infirmary__in=infirmaries)

    if search_term:
        search_filters = (
            Q(visitor__name__icontains=search_term)
            | Q(visitor__relationship__icontains=search_term)
            | Q(reason__icontains=search_term)
            | Q(treatment__icontains=search_term)
            | Q(notes__icontains=search_term)
            | Q(infirmary__icontains=search_term)
            | Q(nurse__icontains=search_term)
        )
        try:
            search_date = datetime.strptime(search_term, '%d/%m/%Y').date()
            search_filters |= Q(date__date=search_date)
        except ValueError:
            pass
        filters &= search_filters

    return VisitorAppointment.objects.filter(filters).select_related('visitor')


def get_all_appointments(date_begin, date_end, infirmaries, search_term):
    """
    Return a unified sorted list of dicts for all appointment types within the
    given date range and infirmaries, optionally filtered by search_term.
    """
    logger.debug(f"get_all_appointments: {date_begin} → {date_end}, infirmaries={infirmaries}")

    student_qs = _get_student_appointments(date_begin, date_end, infirmaries, search_term)
    employee_qs = _get_employee_appointments(date_begin, date_end, infirmaries, search_term)
    visitor_qs = _get_visitor_appointments(date_begin, date_end, infirmaries, search_term)

    all_appointments = []

    for appt in student_qs:
        all_appointments.append({
            'type': 'Estudante',
            'name': appt.student.name,
            'additional_info_label': 'Turma',
            'additional_info': appt.student.class_group.name if appt.student.class_group else '',
            'age': appt.student.age,
            'gender': appt.student.gender,
            'date': appt.date,
            'reason': appt.reason,
            'treatment': appt.treatment,
            'notes': appt.notes,
            'infirmary': appt.infirmary,
            'nurse': appt.nurse,
            'current_class': appt.current_class,
            'revaluation': appt.revaluation,
            'contact_parents': appt.contact_parents,
        })

    for appt in employee_qs:
        all_appointments.append({
            'type': 'Funcionário',
            'name': appt.employee.name,
            'additional_info_label': 'Departamento',
            'additional_info': appt.employee.department.name if appt.employee.department else '',
            'age': appt.employee.age,
            'gender': appt.employee.gender,
            'date': appt.date,
            'reason': appt.reason,
            'treatment': appt.treatment,
            'notes': appt.notes,
            'infirmary': appt.infirmary,
            'nurse': appt.nurse,
            'current_class': '',
            'revaluation': appt.revaluation,
            'contact_parents': '',
        })

    for appt in visitor_qs:
        all_appointments.append({
            'type': 'Visitante',
            'name': appt.visitor.name,
            'additional_info_label': 'Relacionamento',
            'additional_info': appt.visitor.relationship,
            'age': appt.visitor.age,
            'gender': appt.visitor.gender,
            'date': appt.date,
            'reason': appt.reason,
            'treatment': appt.treatment,
            'notes': appt.notes,
            'infirmary': appt.infirmary,
            'nurse': appt.nurse,
            'current_class': '',
            'revaluation': appt.revaluation,
            'contact_parents': '',
        })

    all_appointments.sort(key=lambda x: x['date'], reverse=True)
    return all_appointments


def get_nurse_appointments_current_year():
    """
    Return a list of {'nurse': str, 'count': int} for the current year,
    combining all three appointment types.
    """
    current_year = timezone.now().year
    nurse_counts = defaultdict(int)

    for model in (StudentAppointment, EmployeeAppointment, VisitorAppointment):
        for appt in model.objects.filter(date__year=current_year):
            nurse_counts[appt.nurse] += 1

    return [{'nurse': nurse, 'count': count} for nurse, count in nurse_counts.items()]


def get_total_appointments_current_year():
    """Return the total number of appointments across all types for the current year."""
    current_year = timezone.now().year
    return sum(
        model.objects.filter(date__year=current_year).count()
        for model in (StudentAppointment, EmployeeAppointment, VisitorAppointment)
    )


def get_total_appointments_today():
    """Return the total number of appointments across all types for today."""
    today = timezone.now().date()
    return sum(
        model.objects.filter(date__date=today).count()
        for model in (StudentAppointment, EmployeeAppointment, VisitorAppointment)
    )


def get_total_appointments_infirmary_current_year(infirmary):
    """Return total appointments for a specific infirmary in the current year. Returns 0 if infirmary is falsy."""
    if not infirmary:
        return 0
    current_year = timezone.now().year
    name = infirmary.strip()
    return sum(
        model.objects.filter(date__year=current_year, infirmary__iexact=name).count()
        for model in (StudentAppointment, EmployeeAppointment, VisitorAppointment)
    )


def get_total_appointments_infirmary_today(infirmary):
    """Return total appointments for a specific infirmary today. Returns 0 if infirmary is falsy."""
    if not infirmary:
        return 0
    today = timezone.now().date()
    name = infirmary.strip()
    return sum(
        model.objects.filter(date__date=today, infirmary__iexact=name).count()
        for model in (StudentAppointment, EmployeeAppointment, VisitorAppointment)
    )
