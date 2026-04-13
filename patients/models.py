from django.db import models



#### ----------------- Students models ----------------- ####
class ClassGroup(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    segment = models.CharField(max_length=50, blank=True)
    director = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.name

class Student(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField(blank=True)
    gender = models.CharField(max_length=10)
    email = models.EmailField(null=True, blank=True)
    registry = models.CharField(max_length=20, unique=True)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.SET_NULL, null=True, related_name='students')
    birth_date = models.DateTimeField(null=True, blank=True)
    father_name = models.CharField(max_length=100, null=True, blank=True)
    father_phone = models.CharField(max_length=20, null=True, blank=True)
    mother_name = models.CharField(max_length=100, null=True, blank=True)
    mother_phone = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    

    def __str__(self):
        return self.name

class StudentInfo(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='info', blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    patient_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Info for {self.student.name}"
    







#### ----------------- Employee models ----------------- ####

class Department(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=255)
    director = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Employee(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField(blank=True)
    gender = models.CharField(max_length=10)
    email = models.EmailField(null=True, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    position = models.CharField(max_length=50, null=True, blank=True)
    registry = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class EmployeeInfo(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='info', blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    patient_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Info for {self.employee.name}"






#### ----------------- Visitor models ----------------- ####
class Visitor(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    age = models.IntegerField(blank=True)
    gender = models.CharField(max_length=10)
    email = models.EmailField(unique=True)
    relationship = models.CharField(max_length=50)
    allergies = models.TextField(blank=True, null=True)
    patient_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

