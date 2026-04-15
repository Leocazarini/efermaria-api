import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    EmployeeAppointmentCreateSerializer,
    EmployeeAppointmentSerializer,
    StudentAppointmentCreateSerializer,
    StudentAppointmentSerializer,
    VisitorAppointmentCreateSerializer,
    VisitorAppointmentSerializer,
)
from .services import (
    create_employee_appointment,
    create_student_appointment,
    create_visitor_appointment,
    get_appointments_by_patient,
)
from .models import StudentAppointment, EmployeeAppointment, VisitorAppointment

logger = logging.getLogger('appointments.api_views')


# ──────────────────────────────────────────────
# Student appointments
# ──────────────────────────────────────────────

class StudentAppointmentView(APIView):
    def post(self, request):
        serializer = StudentAppointmentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            appointment = create_student_appointment(
                student_id=data['student_id'],
                infirmary=data['infirmary'],
                nurse=data['nurse'],
                date=data['date'],
                reason=data['reason'],
                treatment=data['treatment'],
                current_class=data['current_class'],
                contact_parents=data['contact_parents'],
                notes=data.get('notes'),
                revaluation=data['revaluation'],
                allergies=data.get('allergies'),
                patient_notes=data.get('patient_notes'),
            )
        except ObjectDoesNotExist:
            return Response({'detail': 'Aluno não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            StudentAppointmentSerializer(appointment).data,
            status=status.HTTP_201_CREATED,
        )


class StudentAppointmentListView(APIView):
    def get(self, request, student_id):
        appointments = get_appointments_by_patient(
            StudentAppointment, 'student_id', student_id
        )
        return Response(appointments)


# ──────────────────────────────────────────────
# Employee appointments
# ──────────────────────────────────────────────

class EmployeeAppointmentView(APIView):
    def post(self, request):
        serializer = EmployeeAppointmentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            appointment = create_employee_appointment(
                employee_id=data['employee_id'],
                infirmary=data['infirmary'],
                nurse=data['nurse'],
                date=data['date'],
                reason=data['reason'],
                treatment=data['treatment'],
                notes=data.get('notes'),
                revaluation=data['revaluation'],
                allergies=data.get('allergies'),
                patient_notes=data.get('patient_notes'),
            )
        except ObjectDoesNotExist:
            return Response({'detail': 'Funcionário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(
            EmployeeAppointmentSerializer(appointment).data,
            status=status.HTTP_201_CREATED,
        )


class EmployeeAppointmentListView(APIView):
    def get(self, request, employee_id):
        appointments = get_appointments_by_patient(
            EmployeeAppointment, 'employee_id', employee_id
        )
        return Response(appointments)


# ──────────────────────────────────────────────
# Visitor appointments
# ──────────────────────────────────────────────

class VisitorAppointmentView(APIView):
    def post(self, request):
        serializer = VisitorAppointmentCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        try:
            appointment = create_visitor_appointment(
                visitor_data=data['visitor'],
                infirmary=data['infirmary'],
                nurse=data['nurse'],
                date=data['date'],
                reason=data['reason'],
                treatment=data['treatment'],
                notes=data.get('notes'),
                revaluation=data['revaluation'],
            )
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            VisitorAppointmentSerializer(appointment).data,
            status=status.HTTP_201_CREATED,
        )


class VisitorAppointmentListView(APIView):
    def get(self, request, visitor_id):
        appointments = get_appointments_by_patient(
            VisitorAppointment, 'visitor_id', visitor_id
        )
        return Response(appointments)
