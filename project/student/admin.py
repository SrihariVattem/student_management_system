from django.contrib import admin
from .models import Teacher, Student, Subject, Attendance, ExamRegistration, StudentPerformance, Exam

# Register Teacher model
admin.site.register(Teacher)

# Register Student model
admin.site.register(Student)

# Register Subject model
admin.site.register(Subject)

# Register Attendance model
admin.site.register(Attendance)

# Register Exam Registration model
admin.site.register(ExamRegistration)

# Register Student Performance model
admin.site.register(StudentPerformance)

admin.site.register(Exam)
