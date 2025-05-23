from django.contrib import admin
from .models import UserProfile, AuditTrail, PasswordResetRequest

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'phone_number', 'is_email_verified')
    list_filter = ('user_type', 'is_email_verified')
    search_fields = ('user__username', 'user__email', 'phone_number')

@admin.register(AuditTrail)
class AuditTrailAdmin(admin.ModelAdmin):
    list_display = ('audit_id', 'user', 'action', 'module', 'action_time', 'ip_address')
    list_filter = ('action', 'module', 'action_time')
    search_fields = ('user__username', 'description', 'ip_address')
    date_hierarchy = 'action_time'
    readonly_fields = ('user', 'action', 'action_time', 'ip_address', 'user_agent', 'module', 'record_id', 'description')

@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'user', 'status', 'requested_at', 'processed_at', 'processed_by')
    list_filter = ('status', 'requested_at', 'processed_at')
    search_fields = ('user__username', 'user__email', 'notes')
    readonly_fields = ('request_id', 'user', 'requested_at')
    date_hierarchy = 'requested_at'
