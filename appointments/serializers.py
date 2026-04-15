from rest_framework import serializers

from .models import StudentAppointment, EmployeeAppointment, VisitorAppointment


class StudentAppointmentCreateSerializer(serializers.Serializer):
    student_id = serializers.CharField()
    infirmary = serializers.CharField()
    nurse = serializers.CharField()
    date = serializers.DateTimeField()
    reason = serializers.CharField()
    treatment = serializers.CharField()
    current_class = serializers.CharField()
    contact_parents = serializers.BooleanField(default=False)
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    revaluation = serializers.BooleanField(default=False)
    allergies = serializers.CharField(required=False, allow_blank=True, allow_null=True, default=None)
    patient_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True, default=None)


class StudentAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAppointment
        fields = '__all__'


class EmployeeAppointmentCreateSerializer(serializers.Serializer):
    employee_id = serializers.CharField()
    infirmary = serializers.CharField()
    nurse = serializers.CharField()
    date = serializers.DateTimeField()
    reason = serializers.CharField()
    treatment = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    revaluation = serializers.BooleanField(default=False)
    allergies = serializers.CharField(required=False, allow_blank=True, allow_null=True, default=None)
    patient_notes = serializers.CharField(required=False, allow_blank=True, allow_null=True, default=None)


class EmployeeAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeAppointment
        fields = '__all__'


class VisitorDataSerializer(serializers.Serializer):
    name = serializers.CharField()
    age = serializers.IntegerField()
    gender = serializers.CharField()
    email = serializers.EmailField()
    relationship = serializers.CharField(required=False, allow_blank=True, default='')
    allergies = serializers.CharField(required=False, allow_blank=True, default='')
    patient_notes = serializers.CharField(required=False, allow_blank=True, default='')


class VisitorAppointmentCreateSerializer(serializers.Serializer):
    visitor = VisitorDataSerializer()
    infirmary = serializers.CharField()
    nurse = serializers.CharField()
    date = serializers.DateTimeField()
    reason = serializers.CharField()
    treatment = serializers.CharField()
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    revaluation = serializers.BooleanField(default=False)


class VisitorAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorAppointment
        fields = '__all__'
