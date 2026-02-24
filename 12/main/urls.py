from django.urls import path, include
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('students/', students_list, name='students_list'),
    path('students/<int:student_id>/', student_detail, name='student_detail'),
    path('courses/', courses_list, name='courses_list'),
    path('courses/<int:course_id>', course_detail, name='course_detail'),
    path('journal/', journal, name='journal')
]