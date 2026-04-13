from django.test import TestCase
from ...models import *

''' 
    
    The following tests are for the models in the patients app.

'''

############################################################################################################

############################################## Student Models ##############################################

class TestClassGroupModel(TestCase):


    def setUp(self):
        self.class_group = ClassGroup.objects.create(
            name='Class 1',
            segment='Primary',
            director='Director 1'
        )

    def test_class_group_model(self):
        class_group = ClassGroup.objects.get(name='Class 1')
        self.assertEqual(class_group.__str__(), 'Class 1')


class TestStudentModel(TestCase):


    def setUp(self):
        self.class_group = ClassGroup.objects.create(
            name='Class 2',
            segment='Secondary',
            director='Director 2'
        )
        self.student = Student.objects.create(
            name='John Doe',
            age=15,
            gender='Male',
            registry='123456',
            class_group=self.class_group,
            birth_date='2009-08-15',
            father_name='John Senior',
            father_phone='555-1234',
            mother_name='Jane Doe',
            mother_phone='555-5678'
        )

    def test_student_model(self):
        student = Student.objects.get(registry='123456')
        self.assertEqual(student.__str__(), 'John Doe')
        self.assertEqual(student.class_group.name, 'Class 2')
        self.assertEqual(student.father_name, 'John Senior')
        self.assertEqual(student.mother_name, 'Jane Doe')


class TestStudentInfoModel(TestCase):


    def setUp(self):
        self.class_group = ClassGroup.objects.create(
            name='Class 3',
            segment='Primary',
            director='Director 1'
        )
        self.student = Student.objects.create(
            name='Jane Doe',
            age=14,
            gender='Female',
            registry='654321',
            class_group=self.class_group,
            birth_date='2010-05-20'
        )
        self.student_info = StudentInfo.objects.create(
            student=self.student,
            allergies='Peanut allergy',
            notes='Requires extra attention in math'
        )

    def test_student_info_model(self):
        student_info = StudentInfo.objects.get(student=self.student)
        self.assertEqual(student_info.__str__(), f"Info for {self.student.name}")
        self.assertEqual(student_info.allergies, 'Peanut allergy')
        self.assertEqual(student_info.notes, 'Requires extra attention in math')
        

############################################################################################################

############################################## Employee Models #############################################

class TestDepartmentModel(TestCase):

    def setUp(self):
        self.department = Department.objects.create(
            name='HR',
            director='Alice Smith'
        )

    def test_department_model(self):
        department = Department.objects.get(name='HR')
        self.assertEqual(department.__str__(), 'HR')
        self.assertEqual(department.director, 'Alice Smith')


class TestEmployeeModel(TestCase):

    def setUp(self):
        self.department = Department.objects.create(
            name='IT',
            director='Bob Johnson'
        )
        self.employee = Employee.objects.create(
            name='John Doe',
            age=30,
            gender='Male',
            birth_date='1994-06-15',
            department=self.department,
            position='Developer',
            registry='EMP123456'
        )

    def test_employee_model(self):
        employee = Employee.objects.get(registry='EMP123456')
        self.assertEqual(employee.__str__(), 'John Doe')
        self.assertEqual(employee.department.name, 'IT')
        self.assertEqual(employee.position, 'Developer')


class TestEmployeeInfoModel(TestCase):

    def setUp(self):
        self.department = Department.objects.create(
            name='Finance',
            director='Carol White'
        )
        self.employee = Employee.objects.create(
            name='Jane Doe',
            age=28,
            gender='Female',
            birth_date='1996-02-20',
            department=self.department,
            position='Accountant',
            registry='EMP654321'
        )
        self.employee_info = EmployeeInfo.objects.create(
            employee=self.employee,
            allergies='None',
            notes='Works remotely'
        )

    def test_employee_info_model(self):
        employee_info = EmployeeInfo.objects.get(employee=self.employee)
        self.assertEqual(employee_info.__str__(), f"Info for {self.employee.name}")
        self.assertEqual(employee_info.allergies, 'None')
        self.assertEqual(employee_info.notes, 'Works remotely')


############################################################################################################

############################################## Visitor Models ##############################################

class TestVisitorModel(TestCase):

    def setUp(self):
        self.visitor = Visitor.objects.create(
            name='Mary Johnson',
            age=45,
            gender='Female',
            relationship='Mother',
            allergies='None',
            notes='Visits once a week'
        )

    def test_visitor_model(self):
        visitor = Visitor.objects.get(name='Mary Johnson')
        self.assertEqual(visitor.__str__(), 'Mary Johnson')
        self.assertEqual(visitor.relationship, 'Mother')
        self.assertEqual(visitor.allergies, 'None')
        self.assertEqual(visitor.notes, 'Visits once a week')



############################################################################################################