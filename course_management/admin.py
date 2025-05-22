from django.contrib import admin
from .models import Course

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('course_id', 'course_name', 'faculty', 'credits')
    list_filter = ('credits',)
    search_fields = ('course_name', 'course_id')
    ordering = ('course_id',)
