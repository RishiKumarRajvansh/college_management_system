from django.contrib import admin
from .models import Report, Notification, DatabaseBackup

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('report_id', 'title', 'report_type', 'generated_by', 'generation_date', 'is_scheduled')
    list_filter = ('report_type', 'is_scheduled', 'generation_date')
    search_fields = ('title', 'description')
    date_hierarchy = 'generation_date'
    readonly_fields = ('generation_date', 'last_run')
    
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'notification_type', 'created_at', 'read')
    list_filter = ('notification_type', 'read', 'created_at')
    search_fields = ('message', 'user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'read_at')

@admin.register(DatabaseBackup)
class DatabaseBackupAdmin(admin.ModelAdmin):
    list_display = ('backup_id', 'backup_date', 'backup_size', 'is_automatic', 'status', 'created_by')
    list_filter = ('backup_date', 'is_automatic', 'status')
    search_fields = ('backup_file', 'notes')
    date_hierarchy = 'backup_date'
    readonly_fields = ('backup_id', 'backup_date')
    fieldsets = (
        ('Backup Information', {
            'fields': ('backup_file', 'backup_date', 'backup_size', 'status')
        }),
        ('Additional Details', {
            'fields': ('created_by', 'is_automatic', 'notes')
        }),
    )
