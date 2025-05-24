from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'code', 'name', 'faculty', 'credits', 'is_active')
    list_filter = ('credits', 'is_active', 'faculty')
    search_fields = ('code', 'name', 'description')
    ordering = ('code', 'name')
