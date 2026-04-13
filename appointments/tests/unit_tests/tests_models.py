from django.test import TestCase
from ...models import *


''' 
    The following tests are for the models in the appointments app.

'''


############################################################################################################

############################################## Infirmary Models ############################################


class TestInfirmaryModel(TestCase):

    def setUp(self):
        self.infirmary = Infirmary.objects.create(
            name='Main Infirmary',
            location='Building A, Floor 1'
        )

    def test_infirmary_model(self):
        infirmary = Infirmary.objects.get(name='Main Infirmary')
        self.assertEqual(infirmary.__str__(), 'Main Infirmary')
        self.assertEqual(infirmary.location, 'Building A, Floor 1')


class TestNurseModel(TestCase):

    def setUp(self):
        self.nurse = Nurse.objects.create(
            name='Nurse Joy',
            username='njoy',
            badge_number='N12345'
        )

    def test_nurse_model(self):
        nurse = Nurse.objects.get(badge_number='N12345')
        self.assertEqual(nurse.__str__(), 'Nurse Joy')
        self.assertEqual(nurse.username, 'njoy')


############################################################################################################

############################################## Appointment Models ##########################################

class TestStudentAppointmentModel(TestCase):

    def setUp(self):
        self.student = Student.objects.create(
            name='John Doe',
            age=16,
            gender='Male',
            registry='S123456'
        )
        self.student_info = StudentInfo.objects.create(
            student=self.student,
            allergies='None',
            notes='Needs regular check-ups'
        )
        self.infirmary = Infirmary.objects.create(
            name='Main Infirmary',
            location='Building A, Floor 1'
        )
        self.nurse = Nurse.objects.create(
            name='Nurse Joy',
            username='njoy',
            badge_number='N12345'
        )
        self.appointment = StudentAppointment.objects.create(
            student=self.student,
            student_info=self.student_info,
            infirmary=self.infirmary,
            nurse=self.nurse,
            date= '2024-08-15 10:00:00',
            current_class='Class 2',
            reason='Headache',
            treatment='Pain relief medication',
            notes='Student reported feeling better',
            revaluation=False,
            contact_parents=False
        )

    def test_student_appointment_model(self):
        appointment = StudentAppointment.objects.get(student=self.student)
        self.assertEqual(appointment.__str__(), f"{self.student.name} - {appointment.date}")
        self.assertEqual(appointment.reason, 'Headache')
        self.assertEqual(appointment.treatment, 'Pain relief medication')
        self.assertEqual(appointment.nurse.name, 'Nurse Joy')


class TestEmployeeAppointmentModel(TestCase):

    def setUp(self):
        self.employee = Employee.objects.create(
            name='Jane Doe',
            age=30,
            gender='Female',
            registry='E123456'
        )
        self.employee_info = EmployeeInfo.objects.create(
            employee=self.employee,
            allergies='Pollen',
            notes='Asthma patient'
        )
        self.infirmary = Infirmary.objects.create(
            name='Main Infirmary',
            location='Building A, Floor 1'
        )
        self.nurse = Nurse.objects.create(
            name='Nurse Joy',
            username='njoy',
            badge_number='N12345'
        )
        self.appointment = EmployeeAppointment.objects.create(
            employee=self.employee,
            employee_info=self.employee_info,
            infirmary=self.infirmary,
            nurse=self.nurse,
            date='2024-08-15 11:00:00',
            reason='Asthma attack',
            treatment='Inhaler administration',
            notes='Patient stabilized',
            revaluation=True
        )

    def test_employee_appointment_model(self):
        appointment = EmployeeAppointment.objects.get(employee=self.employee)
        self.assertEqual(appointment.__str__(), f"{self.employee.name} - {appointment.date}")
        self.assertEqual(appointment.reason, 'Asthma attack')
        self.assertEqual(appointment.treatment, 'Inhaler administration')
        self.assertEqual(appointment.revaluation, True)


class TestVisitorAppointmentModel(TestCase):

    def setUp(self):
        self.visitor = Visitor.objects.create(
            name='Tom Brown',
            age=50,
            gender='Male',
            relationship='Father'
        )
        self.infirmary = Infirmary.objects.create(
            name='Main Infirmary',
            location='Building A, Floor 1'
        )
        self.nurse = Nurse.objects.create(
            name='Nurse Joy',
            username='njoy',
            badge_number='N12345'
        )
        self.appointment = VisitorAppointment.objects.create(
            visitor=self.visitor,
            infirmary=self.infirmary,
            nurse=self.nurse,
            date='2024-08-15 12:00:00',
            reason='Stomach pain',
            treatment='Antacid medication',
            notes='Visitor left feeling better',
            revaluation=False
        )

    def test_visitor_appointment_model(self):
        appointment = VisitorAppointment.objects.get(visitor=self.visitor)
        self.assertEqual(appointment.__str__(), f"{self.visitor.name} - {appointment.date}")
        self.assertEqual(appointment.reason, 'Stomach pain')
        self.assertEqual(appointment.treatment, 'Antacid medication')
        self.assertEqual(appointment.nurse.name, 'Nurse Joy')


############################################################################################################