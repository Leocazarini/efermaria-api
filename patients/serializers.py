from rest_framework import serializers

from .models import ClassGroup, Student, StudentInfo, Department, Employee, EmployeeInfo, Visitor


class ClassGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassGroup
        fields = ['id', 'name', 'segment', 'director']


class StudentInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentInfo
        fields = ['allergies', 'patient_notes']


class StudentSerializer(serializers.ModelSerializer):
    class_group = ClassGroupSerializer(read_only=True)
    info = StudentInfoSerializer(read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'name', 'age', 'gender', 'email', 'registry',
            'class_group', 'birth_date',
            'father_name', 'father_phone', 'mother_name', 'mother_phone',
            'created_at', 'updated_at', 'info',
        ]
        read_only_fields = ['created_at', 'updated_at']


class StudentInfoUpdateSerializer(serializers.Serializer):
    allergies = serializers.CharField(required=False, allow_blank=True, default='')
    patient_notes = serializers.CharField(required=False, allow_blank=True, default='')


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'director']


class EmployeeInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeInfo
        fields = ['allergies', 'patient_notes']


class EmployeeSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    info = EmployeeInfoSerializer(read_only=True)

    class Meta:
        model = Employee
        fields = [
            'id', 'name', 'age', 'gender', 'email', 'registry',
            'department', 'position', 'birth_date',
            'created_at', 'updated_at', 'info',
        ]
        read_only_fields = ['created_at', 'updated_at']


class EmployeeInfoUpdateSerializer(serializers.Serializer):
    allergies = serializers.CharField(required=False, allow_blank=True, default='')
    patient_notes = serializers.CharField(required=False, allow_blank=True, default='')


class VisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = [
            'id', 'name', 'age', 'gender', 'email', 'relationship',
            'allergies', 'patient_notes', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
