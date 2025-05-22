from django.contrib import admin
from .models import Faculty

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('faculty_id', 'name', 'email', 'department')
    list_filter = ('department',)
    search_fields = ('name', 'email', 'faculty_id')
    ordering = ('faculty_id',)
