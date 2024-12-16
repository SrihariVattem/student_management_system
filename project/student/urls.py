# student/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),  # Root URL mapped to login view
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.student_home, name='student_home'),
    path('student-dashboard/<int:student_id>/', views.student_dashboard, name='student_dashboard'),
    path('exam-registration/<int:student_id>/', views.exam_registration, name='exam_registration'),
    path('exam-results/<int:student_id>/', views.exam_results, name='exam_results'),
    path('student/<int:student_id>/tests/', views.tests, name='tests'),
    path('subjects/<int:student_id>/', views.subjects_view, name='subjects'),

]
