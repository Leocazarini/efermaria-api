from django.urls import path

from .api_views import (
    EmployeeByRegistryView,
    EmployeeDetailView,
    EmployeeInfoUpdateView,
    EmployeeListView,
    StudentByRegistryView,
    StudentDetailView,
    StudentInfoUpdateView,
    StudentListView,
    VisitorDetailView,
    VisitorListView,
)

urlpatterns = [
    # Students
    path('students/', StudentListView.as_view(), name='student-list'),
    path('students/<str:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('students/registry/<str:registry>/', StudentByRegistryView.as_view(), name='student-by-registry'),
    path('students/<str:pk>/info/', StudentInfoUpdateView.as_view(), name='student-info-update'),

    # Employees
    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('employees/<str:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/registry/<str:registry>/', EmployeeByRegistryView.as_view(), name='employee-by-registry'),
    path('employees/<str:pk>/info/', EmployeeInfoUpdateView.as_view(), name='employee-info-update'),

    # Visitors
    path('visitors/', VisitorListView.as_view(), name='visitor-list'),
    path('visitors/<int:pk>/', VisitorDetailView.as_view(), name='visitor-detail'),
]
