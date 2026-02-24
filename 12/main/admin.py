from django.contrib import admin
from .models import *
from django.db.models import Avg
# Register your models here.

# admin.site.register(Course)
# admin.site.register(Grade)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('surname', 'name', 'gender', 'short_name', 'age', 'average_grade')
    list_display_links = ('surname', 'name')
    #list_editable = ('edit_surname', 'edit_name')
    search_fields = ('surname', 'name')
    list_filter = ('gender', 'active')

    def average_grade(self, obj):
        res = Grade.objects.filter(student=obj).aggregate(Avg('grade', default=0))
        return res['grade__avg']
    
    def short_name(self, obj):
        return f'{obj.surname} {obj.name[0]}.'
    
    short_name.short_description = 'Короткое имя'

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'course_num', 'start_date', 'end_date')
    list_display_links = ('name', 'course_num')
    search_fields = ('name', 'course_num', 'start_date', 'end_date')
    list_filter = ('name', 'course_num', 'start_date', 'end_date')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('grade', 'date', 'date_add', 'date_update')
    search_fields = ('grade', 'date', 'date_add', 'date_update')
    list_filter = ('grade', 'date', 'date_add', 'date_update')