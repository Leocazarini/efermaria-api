from django.urls import path, include
from . import views

urlpatterns = [ 
    path('student/', views.student_appointment, name='student_appointment'),
    path('student/search/', views.student_identify, name='student_identify'),
    path('student/record/', views.student_record, name='student_record'),

    path('employee/', views.employee_appointment, name='employee_appointment'),
    path('employee/search/', views.employee_identify, name='employee_identify'),
    path('employee/record/', views.employee_record, name='employee_record'),

    path('visitor/', views.visitor_appointment, name='visitor_appointment'),
    path('visitor/search/', views.visitor_identify, name='visitor_identify'),
    path('visitor/record/', views.visitor_record, name='visitor_record'),
]
