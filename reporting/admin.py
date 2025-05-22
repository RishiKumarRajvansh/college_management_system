from django.contrib import admin
from .models import Report

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'title', 'report_type', 'generated_by', 'generation_date', 'is_scheduled')
    list_filter = ('report_type', 'is_scheduled', 'generation_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'generation_date'
    readonly_fields = ('generation_date', 'last_run')
