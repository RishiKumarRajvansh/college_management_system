from django.contrib import admin
from .models import Attendance

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('attendance_id', 'student', 'course', 'date', 'status')
    list_filter = ('date', 'status', 'course')
    search_fields = ('student__name', 'course__course_name')
    ordering = ('-date',)
    date_hierarchy = 'date'
