import logging

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    EmployeeInfoUpdateSerializer,
    EmployeeSerializer,
    StudentInfoUpdateSerializer,
    StudentSerializer,
    VisitorSerializer,
)
from .services import (
    get_employee_by_id,
    get_employee_by_registry,
    get_student_by_id,
    get_student_by_registry,
    get_visitor_by_id,
    search_employees_by_name,
    search_students_by_name,
    search_visitors_by_name,
    upsert_employee_info,
    upsert_student_info,
)

logger = logging.getLogger('patients.api_views')


# ──────────────────────────────────────────────
# Students
# ──────────────────────────────────────────────

class StudentListView(APIView):
    def get(self, request):
        name = request.query_params.get('name', '').strip()
        if not name:
            return Response(
                {'detail': "O parâmetro 'name' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            students = search_students_by_name(name)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)


class StudentDetailView(APIView):
    def get(self, request, pk):
        try:
            student = get_student_by_id(pk)
        except ObjectDoesNotExist:
            return Response({'detail': 'Aluno não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StudentSerializer(student)
        return Response(serializer.data)


class StudentByRegistryView(APIView):
    def get(self, request, registry):
        try:
            student = get_student_by_registry(registry)
        except ObjectDoesNotExist:
            return Response({'detail': 'Aluno não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = StudentSerializer(student)
        return Response(serializer.data)


class StudentInfoUpdateView(APIView):
    def patch(self, request, pk):
        serializer = StudentInfoUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            info = upsert_student_info(
                pk,
                serializer.validated_data['allergies'],
                serializer.validated_data['patient_notes'],
            )
        except ObjectDoesNotExist:
            return Response({'detail': 'Aluno não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'allergies': info.allergies, 'patient_notes': info.patient_notes})


# ──────────────────────────────────────────────
# Employees
# ──────────────────────────────────────────────

class EmployeeListView(APIView):
    def get(self, request):
        name = request.query_params.get('name', '').strip()
        if not name:
            return Response(
                {'detail': "O parâmetro 'name' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            employees = search_employees_by_name(name)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)


class EmployeeDetailView(APIView):
    def get(self, request, pk):
        try:
            employee = get_employee_by_id(pk)
        except ObjectDoesNotExist:
            return Response({'detail': 'Funcionário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)


class EmployeeByRegistryView(APIView):
    def get(self, request, registry):
        try:
            employee = get_employee_by_registry(registry)
        except ObjectDoesNotExist:
            return Response({'detail': 'Funcionário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = EmployeeSerializer(employee)
        return Response(serializer.data)


class EmployeeInfoUpdateView(APIView):
    def patch(self, request, pk):
        serializer = EmployeeInfoUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        try:
            info = upsert_employee_info(
                pk,
                serializer.validated_data['allergies'],
                serializer.validated_data['patient_notes'],
            )
        except ObjectDoesNotExist:
            return Response({'detail': 'Funcionário não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        return Response({'allergies': info.allergies, 'patient_notes': info.patient_notes})


# ──────────────────────────────────────────────
# Visitors
# ──────────────────────────────────────────────

class VisitorListView(APIView):
    def get(self, request):
        name = request.query_params.get('name', '').strip()
        if not name:
            return Response(
                {'detail': "O parâmetro 'name' é obrigatório."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            visitors = search_visitors_by_name(name)
        except ValueError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        serializer = VisitorSerializer(visitors, many=True)
        return Response(serializer.data)


class VisitorDetailView(APIView):
    def get(self, request, pk):
        try:
            visitor = get_visitor_by_id(pk)
        except ObjectDoesNotExist:
            return Response({'detail': 'Visitante não encontrado.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = VisitorSerializer(visitor)
        return Response(serializer.data)
