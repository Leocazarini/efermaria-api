from django.contrib import admin
from .models import *


# Register your models here.

admin.site.register(StudentAppointment)
admin.site.register(EmployeeAppointment)
admin.site.register(VisitorAppointment)