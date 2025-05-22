from django.contrib import admin
from .models import Examination, Result

@admin.register(Examination)
class ExaminationAdmin(admin.ModelAdmin):
    list_display = ('exam_id', 'exam_name', 'course', 'exam_type', 'date', 'total_marks', 'passing_marks')
    list_filter = ('exam_type', 'course')
    search_fields = ('exam_name', 'course__course_name')
    date_hierarchy = 'date'

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('result_id', 'student', 'examination', 'marks_obtained', 'percentage', 'grade', 'status')
    list_filter = ('status', 'grade', 'examination')
    search_fields = ('student__name', 'examination__exam_name')
    readonly_fields = ('percentage', 'grade', 'status')
