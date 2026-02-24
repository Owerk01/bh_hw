from django.shortcuts import render, get_object_or_404
from .models import Student, Course, Grade

# Create your views here.

def index(r):
    return render(r, 'main/index.html')

def students_list(r):
    students = Student.objects.all()
    return render(r, 'main/students_list.html',
                  context={'students':students})

def student_detail(r, student_id):
    student = get_object_or_404(Student, id=student_id)
    return render(r, 'main/student_detail.html',
                  context={'student':student})

def courses_list(r):
    courses = Course.objects.all()
    return render(r, 'main/courses_list.html',
                  context={'courses':courses})

def course_detail(r, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(r, 'main/course_detail.html',
                  context = {'course': course})

def journal(r):
    grades = Grade.objects.all()
    return render(r, 'main/journal.html',
                  context={'grades':grades})