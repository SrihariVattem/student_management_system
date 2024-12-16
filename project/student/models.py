from django.db import models
from django.contrib.auth.hashers import make_password
# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


# Teacher Model
class Teacher(models.Model):

    name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Student Model
class Student(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    grade = models.CharField(max_length=10)
    parent_contact = models.CharField(max_length=15)
    course = models.CharField(max_length=100, null=True, blank=True)
    year= models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),


    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Hash the password before saving if it's not already hashed
        if self.password and not self.password.startswith('pbkdf2_'):
            self.password = make_password(self.password)
        super(Student, self).save(*args, **kwargs)
    def __str__(self):
        return self.name


# Subject Model
class Subject(models.Model):
    name = models.CharField(max_length=100)
    teacher_in_charge = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    exam_type = models.CharField(max_length=100, default='Unkown')


    def __str__(self):
        return self.name


# Attendance Model (Percentage-based attendance with validation)
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    attendance_percentage = models.PositiveIntegerField()

    def clean(self):
        if not (0 <= self.attendance_percentage <= 100):
            raise ValidationError("Attendance percentage must be between 0 and 100.")

    def __str__(self):
        return f"{self.student.name} - {self.date} - {self.attendance_percentage}%"



# Exam Registration Model
class ExamRegistration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    exam_date = models.DateField()
    exam_type = models.CharField(max_length=100, default='Unkown')  # Add this line to store exam type
    status = models.CharField(
        max_length=20,
        choices=[('Registered', 'Registered'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')]
    )

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.exam_type} - {self.status}"


# Student Performance (Grades) Model
class StudentPerformance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    marks_obtained = models.FloatField()
    exam_date = models.DateField()
    is_attempted = models.BooleanField(default=False,blank=True)

    def __str__(self):
        return f"{self.student.name} - {self.subject.name} - {self.marks_obtained}"
class Exam(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)  # Link to Subject
    exam_date = models.DateField()
    exam_type = models.CharField(max_length=100)  # E.g., 'Midterm', 'Final'
    duration = models.PositiveIntegerField()  # Duration in minutes

    def __str__(self):
        return f"{self.subject.name} Exam"