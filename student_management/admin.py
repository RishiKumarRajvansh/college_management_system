from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'name', 'email', 'course', 'year')
    list_filter = ('year', 'course')
    search_fields = ('name', 'email', 'student_id')
    ordering = ('student_id',)
