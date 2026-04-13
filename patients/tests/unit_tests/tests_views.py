from django.test import TestCase, Client
from django.http import JsonResponse
from django.urls import reverse
from patients.models import Student, StudentInfo, ClassGroup
from ...views import *
import json



'''
    Unit tests for the views.py file

'''



################################ Student Views ################################
class TestCreateStudents(TestCase):

    def setUp(self):
        self.valid_data = [
            {
                'name': 'John Doe',
                'age': 15,
                'gender': 'Male',
                'registry': 'S123456',

            },
            {
                'name': 'Jane Doe',
                'age': 14,
                'gender': 'Female',
                'registry': 'S654321',

            }
        ]
        self.invalid_data_format = {
            'name': 'John Doe',
            'age': 15,
            'gender': 'Male',
            'registry': 'S123456',

        }
        self.no_data = None

    def test_create_students_success(self):
        response = create_students(self.valid_data)
        self.assertEqual(response['status'], 'success')
        self.assertEqual(Student.objects.count(), 2)

    def test_create_students_invalid_data_format(self):
        response = create_students(self.invalid_data_format)
        self.assertEqual(response['status'], 'error')
        self.assertEqual(response['message'], 'Invalid data format, expected a list of objects')

    def test_create_students_no_data_provided(self):
        response = create_students(self.no_data)
        self.assertEqual(response['status'], 'error')
        self.assertEqual(response['message'], 'No data provided')

class TestCreateStudentInfo(TestCase):

    def setUp(self):
        self.client = Client()
        self.class_group = ClassGroup.objects.create(
            name='Class 1',
            segment='Primary',
            director='Director 1'
        )
        self.student = Student.objects.create(
            name='John Doe',
            age=15,
            gender='Male',
            registry='S123456',
            class_group=self.class_group
        )
        self.valid_data_new = json.dumps({
            'student_id': self.student.id,  # Mudança para 'student_id'
            'allergies': 'Peanuts',
            'notes': 'Carries EpiPen'
        })
        self.valid_data_update = json.dumps({
            'student_id': self.student.id,  # Mudança para 'student_id'
            'allergies': 'Peanuts and Shellfish',
            'notes': 'Carries EpiPen and requires regular check-ups'
        })
        self.invalid_data_format = json.dumps([{
            'student_id': self.student.id,
            'allergies': 'Peanuts',
            'notes': 'Carries EpiPen'
        }])
        self.invalid_json = "{'student_id': " + str(self.student.id) + ", 'allergies': 'Peanuts', 'notes': 'Carries EpiPen'"  # JSON malformado

    def test_create_student_info_success(self):
        url = reverse('create_student_info')
        response = self.client.post(url, data=self.valid_data_new, content_type='application/json')
        self.assertEqual(response.status_code, 200)  # Mudança de 201 para 200
        self.assertEqual(StudentInfo.objects.count(), 1)
        self.assertEqual(StudentInfo.objects.first().allergies, 'Peanuts')

    def test_update_student_info_success(self):
        # Primeiro, crie o registro inicial
        self.client.post(reverse('create_student_info'), data=self.valid_data_new, content_type='application/json')
        
        # Em seguida, faça uma atualização
        url = reverse('create_student_info')
        response = self.client.post(url, data=self.valid_data_update, content_type='application/json')
        self.assertEqual(response.status_code, 200)  # Mudança de 201 para 200
        self.assertEqual(StudentInfo.objects.count(), 1)
        self.assertEqual(StudentInfo.objects.first().allergies, 'Peanuts and Shellfish')
        self.assertEqual(StudentInfo.objects.first().notes, 'Carries EpiPen and requires regular check-ups')

    def test_create_student_info_invalid_data_format(self):
        url = reverse('create_student_info')
        response = self.client.post(url, data=self.invalid_data_format, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Invalid data format, expected a dictionary')

    def test_create_student_info_invalid_json(self):
        url = reverse('create_student_info')
        response = self.client.post(url, data=self.invalid_json, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Invalid JSON')

    def test_create_student_info_invalid_request_method(self):
        url = reverse('create_student_info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Invalid request method')
    
class TestCreateClassGroup(TestCase):

    def setUp(self):
        self.client = Client()
        self.valid_data = json.dumps([{
            'name': 'Class 1',
            'segment': 'Primary',
            'director': 'Director 1'
        }, {
            'name': 'Class 2',
            'segment': 'Secondary',
            'director': 'Director 2'
        }])
        self.invalid_data_format = json.dumps({
            'name': 'Class 1',
            'segment': 'Primary',
            'director': 'Director 1'
        })  
        self.empty_data = None  

    def test_create_class_group_success(self):
        
        response = create_class_group(json.loads(self.valid_data))
        self.assertEqual(response['status'], 'success')
        self.assertEqual(ClassGroup.objects.count(), 2)
        self.assertEqual(ClassGroup.objects.first().name, 'Class 1')

    def test_create_class_group_invalid_data_format(self):
        response = create_class_group(json.loads(self.invalid_data_format))
        self.assertEqual(response['status'], 'error')
        self.assertEqual(response['message'], 'Invalid data format, expected a list of objects')

    def test_create_class_group_no_data(self):
        response = create_class_group(self.empty_data)
        self.assertEqual(response['status'], 'error')
        self.assertEqual(response['message'], 'No data provided')

class TestSearchStudent(TestCase):

    def setUp(self):
        self.class_group = ClassGroup.objects.create(
            name='Class 1',
            segment='Primary',
            director='Director 1'
        )
        self.student1 = Student.objects.create(
            name='John Doe',
            age=15,
            gender='Male',
            registry='S123456',
            class_group=self.class_group,
        )
        self.student_info1 = StudentInfo.objects.create(
            student=self.student1,
            allergies='None',
            notes='Regular check-ups'
        )

        self.student2 = Student.objects.create(
            name='Jane Doe',
            age=14,
            gender='Female',
            registry='S654321',
            class_group=self.class_group,
        )
        self.student_info2 = StudentInfo.objects.create(
            student=self.student2,
            allergies='Peanuts',
            notes='Carries EpiPen'
        )

    def test_search_student_success(self):
        response = search_student(name='John Doe', registry='S123456')
        self.assertIsInstance(response, dict)
        self.assertEqual(response['name'], 'John Doe')
        self.assertEqual(response['info']['allergies'], 'None')
        self.assertEqual(response['class_group_name'], 'Class 1')

    def test_search_student_multiple_records(self):
        
        Student.objects.create(
            name='John Doe',
            age=16,
            gender='Male',
            registry='S789012',
            class_group=self.class_group,
        )

        response = search_student(name='John Doe', registry=None)
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['message'], 'More than one record found for the given information.')

    def test_search_student_not_found(self):
        response = search_student(name='Nonexistent Name', registry='NonexistentRegistry')
        self.assertEqual(response, None)

class TestSearchStudentByName(TestCase):

    def setUp(self):
        self.client = Client()
        self.class_group = ClassGroup.objects.create(
            name='Class 1',
            segment='Primary',
            director='Director 1'
        )
        self.student1 = Student.objects.create(
            name='John Doe',
            age=15,
            gender='Male',
            registry='S123456',
            class_group=self.class_group
        )
        self.student2 = Student.objects.create(
            name='Jane Doe',
            age=14,
            gender='Female',
            registry='S654321',
            class_group=self.class_group
        )
        self.student3 = Student.objects.create(
            name='Johnny Smith',
            age=16,
            gender='Male',
            registry='S987654',
            class_group=self.class_group
        )

    def test_search_single_result(self):
        url = reverse('search_student_by_name') + '?q=Jane'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response_data['results'][0]['name'], 'Jane Doe')

    def test_search_multiple_results(self):
        url = reverse('search_student_by_name') + '?q=John'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 2)
        names = [student['name'] for student in response_data['results']]
        self.assertIn('John Doe', names)
        self.assertIn('Johnny Smith', names)

    def test_search_no_results(self):
        url = reverse('search_student_by_name') + '?q=Nonexistent'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 0)

    def test_search_empty_query(self):
        url = reverse('search_student_by_name') + '?q='
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 0)

    def test_search_no_query_parameter(self):
        url = reverse('search_student_by_name')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 0)


################################ Employee Views ################################

class TestCreateEmployees(TestCase):

    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(
            name='HR',
            director='Director HR'
        )
        self.valid_data = json.dumps([{
            'name': 'Alice Smith',
            'age': 30,
            'gender': 'Female',
            'registry': 'E123456',
            'department_id': self.department.id,
            'position': 'HR Manager'
        }, {
            'name': 'Bob Johnson',
            'age': 40,
            'gender': 'Male',
            'registry': 'E654321',
            'department_id': self.department.id,
            'position': 'HR Specialist'
        }])
        self.invalid_data_format = json.dumps({
            'name': 'Alice Smith',
            'age': 30,
            'gender': 'Female',
            'registry': 'E123456',
            'department_id': self.department.id,
            'position': 'HR Manager'
        })  
        self.empty_data = None  

    def test_create_employees_success(self):
        
        response = create_employees(json.loads(self.valid_data))
        self.assertEqual(response['status'], 'success')
        self.assertEqual(Employee.objects.count(), 2)
        self.assertEqual(Employee.objects.first().name, 'Alice Smith')

    def test_create_employees_invalid_data_format(self):
        response = create_employees(json.loads(self.invalid_data_format))
        self.assertEqual(response['status'], 'error')
        self.assertEqual(response['message'], 'Invalid data format, expected a list of objects')

    def test_create_employees_no_data(self):
        response = create_employees(self.empty_data)
        self.assertEqual(response['status'], 'error')
        self.assertEqual(response['message'], 'No data provided')

class TestCreateEmployeeInfo(TestCase):

    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(
            name='IT',
            director='Director IT'
        )
        self.employee = Employee.objects.create(
            name='Alice Smith',
            age=30,
            gender='Female',
            registry='E123456',
            department=self.department,
            position='Software Engineer'
        )
        self.valid_data_new = json.dumps({
            'employee_id': self.employee.id,
            'allergies': 'Peanuts',
            'notes': 'Works remotely'
        })
        self.valid_data_update = json.dumps({
            'employee_id': self.employee.id,
            'allergies': 'Peanuts and Shellfish',
            'notes': 'Works remotely, prefers morning meetings'
        })
        self.invalid_data_format = json.dumps([{
            'employee_id': self.employee.id,
            'allergies': 'Peanuts',
            'notes': 'Works remotely'
        }])  # Dados no formato de lista, inválido
        self.invalid_json = "{'employee_id': " + str(self.employee.id) + ", 'allergies': 'Peanuts', 'notes': 'Works remotely'"  # JSON malformado

    def test_create_employee_info_success(self):
        url = reverse('create_employee_info')
        response = self.client.post(url, data=self.valid_data_new, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmployeeInfo.objects.count(), 1)
        self.assertEqual(EmployeeInfo.objects.first().allergies, 'Peanuts')

    def test_update_employee_info_success(self):
        # Primeiro, crie o registro inicial
        self.client.post(reverse('create_employee_info'), data=self.valid_data_new, content_type='application/json')
        
        # Em seguida, faça uma atualização
        url = reverse('create_employee_info')
        response = self.client.post(url, data=self.valid_data_update, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(EmployeeInfo.objects.count(), 1)
        self.assertEqual(EmployeeInfo.objects.first().allergies, 'Peanuts and Shellfish')
        self.assertEqual(EmployeeInfo.objects.first().notes, 'Works remotely, prefers morning meetings')

    def test_create_employee_info_invalid_data_format(self):
        url = reverse('create_employee_info')
        response = self.client.post(url, data=self.invalid_data_format, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Invalid data format, expected a dictionary')

    def test_create_employee_info_invalid_json(self):
        url = reverse('create_employee_info')
        response = self.client.post(url, data=self.invalid_json, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Invalid JSON')

    def test_create_employee_info_invalid_request_method(self):
        url = reverse('create_employee_info')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Invalid request method')

class TestCreateDepartment(TestCase):

    def setUp(self):
        self.client = Client()
        self.valid_data = json.dumps([{
            'name': 'HR',
            'director': 'John Doe'
        }, {
            'name': 'IT',
            'director': 'Jane Smith'
        }])
        self.invalid_data_format = json.dumps({
            'name': 'HR',
            'director': 'John Doe'
        })  # Não é uma lista, então é inválido
        self.empty_data = None  # Simula dados não fornecidos

    def test_create_department_success(self):
        # Chama a função diretamente já que não foi especificada uma view
        response = create_department(json.loads(self.valid_data))
        self.assertEqual(response['status'], 'success')
        self.assertEqual(Department.objects.count(), 2)
        self.assertEqual(Department.objects.first().name, 'HR')

    def test_create_department_invalid_data_format(self):
        response = create_department(json.loads(self.invalid_data_format))
        self.assertEqual(response['status'], 'error')
        self.assertEqual(response['message'], 'Invalid data format, expected a list of objects')

    def test_create_department_no_data(self):
        response = create_department(self.empty_data)
        self.assertEqual(response['status'], 'error')
        self.assertEqual(response['message'], 'No data provided')

class TestSearchEmployee(TestCase):

    def setUp(self):
        self.department = Department.objects.create(
            name='IT',
            director='John Doe'
        )
        self.employee1 = Employee.objects.create(
            name='Alice Smith',
            age=30,
            gender='Female',
            registry='E123456',
            department=self.department,
            position='Software Engineer'
        )
        self.employee2 = Employee.objects.create(
            name='Alice Johnson',
            age=32,
            gender='Female',
            registry='E654321',
            department=self.department,
            position='System Analyst'
        )
        self.employee_info1 = EmployeeInfo.objects.create(
            employee=self.employee1,
            allergies='Peanuts',
            notes='Works remotely'
        )
        self.employee_info2 = EmployeeInfo.objects.create(
            employee=self.employee2,
            allergies='None',
            notes='Full-time in-office'
        )

    def test_search_single_result(self):
        response = search_employee(name='Alice Smith', registry='E123456')
        self.assertIsInstance(response, dict)
        self.assertEqual(response['name'], 'Alice Smith')
        self.assertEqual(response['info']['allergies'], 'Peanuts')

    def test_search_multiple_results(self):
        response = search_employee(name='Alice', registry=None)
        self.assertIsInstance(response, JsonResponse)
        response_data = json.loads(response.content)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['status'], 'error')
        self.assertEqual(response_data['message'], 'More than one record found for the given information.')

    def test_search_no_results(self):
        response = search_employee(name='Nonexistent', registry='E999999')
        self.assertEqual(response, None)

class TestSearchEmployeeByName(TestCase):

    def setUp(self):
        self.client = Client()
        self.department = Department.objects.create(
            name='IT',
            director='John Doe'
        )
        self.employee1 = Employee.objects.create(
            name='Alice Smith',
            age=30,
            gender='Female',
            registry='E123456',
            department=self.department,
            position='Software Engineer'
        )
        self.employee2 = Employee.objects.create(
            name='Alice Johnson',
            age=32,
            gender='Female',
            registry='E654321',
            department=self.department,
            position='System Analyst'
        )
        self.employee3 = Employee.objects.create(
            name='Bob Smith',
            age=35,
            gender='Male',
            registry='E987654',
            department=self.department,
            position='Network Engineer'
        )

    def test_search_single_result(self):
        url = reverse('search_employee_by_name') + '?q=Alice Smith'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response_data['results'][0]['name'], 'Alice Smith')

    def test_search_multiple_results(self):
        url = reverse('search_employee_by_name') + '?q=Alice'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 2)
        names = [employee['name'] for employee in response_data['results']]
        self.assertIn('Alice Smith', names)
        self.assertIn('Alice Johnson', names)

    def test_search_no_results(self):
        url = reverse('search_employee_by_name') + '?q=Nonexistent'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 0)

    def test_search_empty_query(self):
        url = reverse('search_employee_by_name') + '?q='
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 0)

    def test_search_no_query_parameter(self):
        url = reverse('search_employee_by_name')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 0)


################################ Visitor Views ################################

class TestCreateVisitor(TestCase):

    def setUp(self):
        self.client = Client()
        self.valid_data = json.dumps([{
            'name': 'John Doe',
            'age': 45,
            'gender': 'Male',
            'relationship': 'Father'
        }, {
            'name': 'Jane Doe',
            'age': 42,
            'gender': 'Female',
            'relationship': 'Mother'
        }])
        self.invalid_data_format = json.dumps({
            'name': 'John Doe',
            'age': 45,
            'gender': 'Male',
            'relationship': 'Father'
        })  
        self.invalid_json = "{'name': 'John Doe', 'age': 45, 'gender': 'Male', 'relationship': 'Father'"  # JSON malformado

    def test_create_visitor_success(self):
        url = reverse('create_visitor')
        response = self.client.post(url, data=self.valid_data, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Visitor.objects.count(), 2)
        self.assertEqual(Visitor.objects.first().name, 'John Doe')

    def test_create_visitor_invalid_data_format(self):
        url = reverse('create_visitor')
        response = self.client.post(url, data=self.invalid_data_format, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Invalid data format, expected a list of objects')

    def test_create_visitor_invalid_json(self):
        url = reverse('create_visitor')
        response = self.client.post(url, data=self.invalid_json, content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Invalid JSON')

    def test_create_visitor_invalid_request_method(self):
        url = reverse('create_visitor')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Invalid request method')

class TestSearchVisitor(TestCase):

    def setUp(self):
        self.visitor1 = Visitor.objects.create(
            name='John Doe',
            age=45,
            gender='Male',
            relationship='Father',
            allergies='None',
            notes='Regular visitor'
        )
        self.visitor2 = Visitor.objects.create(
            name='Jane Doe',
            age=42,
            gender='Female',
            relationship='Mother',
            allergies='Peanuts',
            notes='Visits on weekends'
        )

    def test_search_single_visitor(self):
        response = search_visitor(name='John Doe')
        self.assertIsInstance(response, dict)
        self.assertEqual(response['name'], 'John Doe')
        self.assertEqual(response['age'], 45)
        self.assertEqual(response['gender'], 'Male')
        self.assertEqual(response['relationship'], 'Father')
        self.assertEqual(response['allergies'], 'None')
        self.assertEqual(response['notes'], 'Regular visitor')

    def test_search_visitor_not_found(self):
        response = search_visitor(name='Nonexistent Name')
        self.assertEqual(response, None)

class TestSearchVisitorByName(TestCase):

    def setUp(self):
        self.client = Client()
        self.visitor1 = Visitor.objects.create(
            name='John Doe',
            age=45,
            gender='Male',
            relationship='Father',
            allergies='None',
            notes='Regular visitor'
        )
        self.visitor2 = Visitor.objects.create(
            name='Jane Doe',
            age=42,
            gender='Female',
            relationship='Mother',
            allergies='Peanuts',
            notes='Visits on weekends'
        )

    def test_search_single_visitor_by_name(self):
        url = reverse('search_visitor_by_name')
        response = self.client.get(url, {'q': 'John Doe'})
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 1)
        self.assertEqual(response_data['results'][0]['name'], 'John Doe')

    def test_search_multiple_visitors_by_name(self):
        url = reverse('search_visitor_by_name')
        response = self.client.get(url, {'q': 'Doe'})
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 2)

    def test_search_visitor_by_name_not_found(self):
        url = reverse('search_visitor_by_name')
        response = self.client.get(url, {'q': 'Nonexistent Name'})
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 0)

    def test_search_visitor_by_name_empty_query(self):
        url = reverse('search_visitor_by_name')
        response = self.client.get(url, {'q': ''})
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(len(response_data['results']), 0)
