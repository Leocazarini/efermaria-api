from django.urls import path
from .views import *



urlpatterns = [
    path('records/student/', student_record, name='student_record'),
    path('records/student/search/', student_search, name='student_search_record'),

    path('records/employee/', employee_record, name='employee_record'),
    path('records/employee/search/', employee_search, name='employee_search_record'),

    path('search_reports/', reports, name='search_reports'),



]