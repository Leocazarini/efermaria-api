from django.urls import path

from .api_views import (
    EmployeeAppointmentListView,
    EmployeeAppointmentView,
    StudentAppointmentListView,
    StudentAppointmentView,
    VisitorAppointmentListView,
    VisitorAppointmentView,
)

urlpatterns = [
    # Student appointments
    path('student/', StudentAppointmentView.as_view(), name='appointment-student-create'),
    path('student/<str:student_id>/', StudentAppointmentListView.as_view(), name='appointment-student-list'),

    # Employee appointments
    path('employee/', EmployeeAppointmentView.as_view(), name='appointment-employee-create'),
    path('employee/<str:employee_id>/', EmployeeAppointmentListView.as_view(), name='appointment-employee-list'),

    # Visitor appointments
    path('visitor/', VisitorAppointmentView.as_view(), name='appointment-visitor-create'),
    path('visitor/<int:visitor_id>/', VisitorAppointmentListView.as_view(), name='appointment-visitor-list'),
]
