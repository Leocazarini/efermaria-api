import json
from django.test import TestCase
from django.http import JsonResponse, Http404
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from patients.models import *
from controller.crud import *


class TestCreateObjects(TestCase):

    def setUp(self):
        self.data_single = [
            {
                'name': 'John Doe',
                'age': 15,
                'gender': 'Male',
                'registry': 'S123456',
            }
        ]
        self.data_multiple = [
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
            },
            {
                'name': 'Bob Smith',
                'age': 16,
                'gender': 'Male',
                'registry': 'S789012',
            }
        ]

    def test_create_single_object(self):
        response = create_objects(Student, self.data_single)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Student.objects.count(), 1)
        student = Student.objects.get(registry='S123456')
        self.assertEqual(student.name, 'John Doe')

    def test_create_multiple_objects(self):
        response = create_objects(Student, self.data_multiple)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Student.objects.count(), len(self.data_multiple))
        for data in self.data_multiple:
            student = Student.objects.get(registry=data['registry'])
            self.assertEqual(student.name, data['name'])


class TestGetObject(TestCase):


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

    def test_get_object_by_name(self):
        
        result = get_object(Student, name='John')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'John Doe')

        result = get_object(Student, name='Doe')
        self.assertEqual(len(result), 2)
        names = [student.name for student in result]
        self.assertIn('John Doe', names)
        self.assertIn('Jane Doe', names)

    def test_get_object_by_registry(self):
        
        result = get_object(Student, registry='S123456')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].registry, 'S123456')
        self.assertEqual(result[0].name, 'John Doe')

        result = get_object(Student, registry='S654321')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].registry, 'S654321')
        self.assertEqual(result[0].name, 'Jane Doe')

    def test_get_object_with_related_fields(self):
        
        result = get_object(Student, name='John', related_fields=['class_group', 'info'])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, 'John Doe')
        self.assertEqual(result[0].class_group.name, 'Class 1')
        self.assertEqual(result[0].info.allergies, 'None')

    def test_get_object_no_records_found(self):
        
        with self.assertRaises(Http404):
            get_object(Student, name='Nonexistent')

        with self.assertRaises(Http404):
            get_object(Student, registry='Nonexistent')


class TestGetById(TestCase):

    def setUp(self):
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
            class_group=self.class_group,
        )
        self.student_info = StudentInfo.objects.create(
            student=self.student,
            allergies='None',
            notes='Regular check-ups'
        )

    def test_get_by_id_success(self):
        result = get_by_id(Student, self.student.pk)
        self.assertEqual(result.pk, self.student.pk)
        self.assertEqual(result.name, 'John Doe')

    def test_get_by_id_not_found(self):
        with self.assertRaises(Http404):
            get_by_id(Student, 999)  # ID inexistente

    def test_get_by_id_with_related_fields(self):
        result = get_by_id(Student, self.student.pk, related_fields=['class_group', 'info'])
        self.assertEqual(result.pk, self.student.pk)
        self.assertEqual(result.class_group.name, 'Class 1')
        self.assertEqual(result.info.allergies, 'None')


class TestUpdateObject(TestCase):

    def setUp(self):
        self.student = Student.objects.create(
            name='John Doe',
            age=15,
            gender='Male',
            registry='S123456',
        )

    def test_update_object_success(self):
        data = {
            'name': 'Johnathan Doe',
            'age': 16,
        }
        response = update_object(Student, 'S123456', data)
        self.assertEqual(response.status_code, 200)
        updated_student = Student.objects.get(registry='S123456')
        self.assertEqual(updated_student.name, 'Johnathan Doe')
        self.assertEqual(updated_student.age, 16)

    def test_update_object_invalid_data(self):
        data = {
            'age': 'invalid_age',  # Providing an invalid data type
        }
        with self.assertRaises(ValueError):
            update_object(Student, 'S123456', data)

    def test_update_object_not_found(self):
        data = {
            'name': 'Jane Doe',
            'age': 17,
        }
        response = update_object(Student, 'NonexistentRegistry', data)
        self.assertEqual(response.status_code, 404)


class TestDeleteObject(TestCase):

    def setUp(self):
        self.student = Student.objects.create(
            name='John Doe',
            age=15,
            gender='Male',
            registry='S123456',
        )

    def test_delete_object_success(self):
        response = delete_object(Student, 'S123456')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Student.objects.count(), 0)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['message'], 'Deleted successfully')

    def test_delete_object_not_found(self):
        response = delete_object(Student, 'NonexistentRegistry')
        self.assertEqual(response.status_code, 404)
        response_data = json.loads(response.content)
        self.assertIn('status', response_data)
        self.assertEqual(response_data['status'], 'error')
        self.assertEqual(response_data['message'], 'Object not found')