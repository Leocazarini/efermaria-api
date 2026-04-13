from django.urls import path
from .views import *
urlpatterns = [
    path('students/create/', create_students, name='create_students'),
    path('students/create/info/', create_student_info, name='create_student_info'),
    path('students/search/', search_student, name='search_student'),
    path('students/search/name/', search_student_by_name, name='search_student_by_name'),
    path('students/search/id/', search_student_by_id, name='search_student_by_id'),

    path('employees/create/', create_employees, name='create_employees'),
    path('employees/create/info/', create_employee_info, name='create_employee_info'),
    path('employees/search/', search_employee, name='search_employee'),
    path('employees/search/name/', search_employee_by_name, name='search_employee_by_name'),
    path('employees/search/id/', search_employee_by_id, name='search_employee_by_id'),

    path('visitors/create/', manage_visitor_data, name='create_visitor'),
    path('visitors/search/', search_visitor, name='search_visitor'),
    path('visitors/search/name/', search_visitor_by_name, name='search_visitor_by_name'),
    path('visitors/search/id/', search_visitor_by_id, name='search_visitor_by_id'),
    
]