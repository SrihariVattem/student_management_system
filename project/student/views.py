from django.shortcuts import render, get_object_or_404
from .models import Student, StudentPerformance, Attendance, Exam, ExamRegistration, Subject
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
from django.contrib import messages
from .models import Student

# Student login view
def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, 'login.html')

        try:
            # Fetch the student by email
            student = Student.objects.get(email=email)

            # Validate the password using check_password
            if check_password(password, student.password):
                # Store the student's ID in the session manually
                request.session['student_id'] = student.id
                return redirect('student_home')  # Redirect to student home page
            else:
                messages.error(request, "Invalid password.")
        except Student.DoesNotExist:
            messages.error(request, "No student found with this email.")
        except Exception as e:
            messages.error(request, f"An unexpected error occurred: {e}")

    return render(request, 'login.html')


# Student logout view
def logout_view(request):
    # Clear the session and logout the user
    request.session.flush()  # Clears all session data, including 'student_id'
    messages.success(request, "You have been logged out.")
    return redirect('login')


# Student home page view - After login
def student_home(request):
    student_id = request.session.get('student_id')

    if not student_id:
        return redirect('login')

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return redirect('login')

    return render(request, 'home.html', {'student': student})


# Student Dashboard view

def student_dashboard(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
        student_performances = StudentPerformance.objects.filter(student=student)
        attendance = Attendance.objects.get(student=student)

        # Calculate attendance percentage
        attendance_percentage = attendance.attendance_percentage
        absent_percentage = 100 - attendance_percentage

        # Calculate pass/fail status for each subject
        performance_status = []
        for performance in student_performances:
            status = 'Pass' if performance.marks_obtained >= 50 else 'Fail'
            performance_status.append({
                'subject': performance.subject.name,
                'marks': performance.marks_obtained,
                'exam_date': performance.exam_date,
                'status': status,
                'teacher': performance.subject.teacher_in_charge.name,  # Get teacher's name
            })

        return render(request, 'student_dashboard.html', {
            'student': student,
            'performance_status': performance_status,
            'attendance_percentage': attendance_percentage,
            'absent_percentage': absent_percentage,
        })

    except Student.DoesNotExist:
        return redirect('login')  # If student doesn't exist, redirect to login page
    except Attendance.DoesNotExist:
        return redirect('student_home')  # If attendance doesn't exist, redirect to student home


def exam_registration(request, student_id):
    student = get_object_or_404(Student, pk=student_id)

    # Get exams that the student has already registered for or attempted
    registered_exam_subjects = ExamRegistration.objects.filter(student=student).values_list('subject', flat=True)
    attempted_exam_subjects = StudentPerformance.objects.filter(student=student, is_attempted=True).values_list('subject', flat=True)

    # Combine both lists (registered and attempted subjects)
    excluded_subjects = set(registered_exam_subjects) | set(attempted_exam_subjects)

    # Filter out exams that the student has already registered for or attempted
    exams_to_display = Exam.objects.exclude(subject__in=excluded_subjects)

    if request.method == 'POST':
        exam_id = request.POST.get('exam_id')
        exam = get_object_or_404(Exam, pk=exam_id)

        # Create the registration entry
        exam_registration = ExamRegistration(
            student=student,
            subject=exam.subject,
            exam_date=exam.exam_date,
            exam_type=exam.exam_type,  # The type of the exam (e.g., 'Midterm', 'Final')
            status='Registered'  # The initial status is 'Registered'
        )
        exam_registration.save()

        # Redirect to the same page or another page (like confirmation)
        return redirect('exam_registration', student_id=student.id)

    return render(request, 'exam_registration.html', {
        'student': student,
        'exams': exams_to_display
    })

def get_grade(marks):
    if marks >= 90:
        return "A+"
    elif marks >= 80:
        return "A"
    elif marks >= 70:
        return "B+"
    elif marks >= 60:
        return "B"
    elif marks >= 50:
        return "C+"
    elif marks >= 40:
        return "C"
    elif marks >= 30:
        return "D"
    else:
        return "F"

def exam_results(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return render(request, 'error.html', {'message': 'Student not found'})

    # Retrieve the student's performance from the StudentPerformance table
    results = StudentPerformance.objects.filter(student=student)

    # Prepare the data to pass to the template
    result_data = []

    for result in results:
        grade = get_grade(result.marks_obtained)  # Get the grade based on marks
        result_data.append({
            'performance': result,
            'subject': result.subject,
            'teacher': result.subject.teacher_in_charge,
            'grade': grade
        })

    context = {
        'student': student,
        'result_data': result_data
    }

    return render(request, 'exam_results.html', context)



def tests(request, student_id):
    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist:
        return render(request, 'error.html', {'message': 'Student not found'})

    # Fetch exams the student is registered for
    registered_exams = ExamRegistration.objects.filter(student=student)

    # Prepare the context with the student and exam data
    context = {
        'student': student,
        'registered_exams': registered_exams
    }

    return render(request, 'tests.html', context)

def subjects_view(request, student_id):
    # Get the student by ID
    student = get_object_or_404(Student, id=student_id)

    # Fetch all subjects
    subjects = Subject.objects.all()
    subject_data = []

    for subject in subjects:
        status = "Not Registered"
        exam_date = None  # Default to None
        exam_type = subject.exam_type  # Get exam type from Subject model

        # Check for registration
        registration = ExamRegistration.objects.filter(student=student, subject=subject).first()
        if registration:
            status = registration.status
            exam_date = registration.exam_date  # Use exam date from registration

        # Check for performance (attempted exams)
        performance = StudentPerformance.objects.filter(student=student, subject=subject).first()
        if performance and performance.is_attempted:
            status = "Attempted"
            exam_date = performance.exam_date  # Use exam date from performance

        # If the student is not registered or attempted, use exam date from the Exam model
        if not exam_date:
            exam = Exam.objects.filter(subject=subject).first()
            if exam:
                exam_date = exam.exam_date  # Use exam date from the Exam model

        subject_data.append({
            "name": subject.name,
            "teacher": subject.teacher_in_charge.name if subject.teacher_in_charge else "N/A",
            "type": exam_type,  # Ensure we are using the exam type from Subject modelS
            "status": status,
            "exam_date": exam_date,
        })

    return render(request, "subjects.html", {"subject_data": subject_data, "student": student})

