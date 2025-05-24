from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notification(models.Model):
    """Model for system notifications"""
    NOTIFICATION_TYPES = (
        ('info', 'Information'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    notification_type = models.CharField(max_length=10, choices=NOTIFICATION_TYPES, default='info')
    link = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message[:30]}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.read = True
        self.read_at = timezone.now()
        self.save()

class Report(models.Model):
    REPORT_TYPES = (
        ('student', 'Student Report'),
        ('faculty', 'Faculty Report'),
        ('attendance', 'Attendance Report'),
        ('examination', 'Examination Report'),
        ('fee', 'Fee Report'),
        ('library', 'Library Report'),
        ('hostel', 'Hostel Report'),
        ('custom', 'Custom Report'),    )
    
    report_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='generated_reports')
    generation_date = models.DateTimeField(auto_now_add=True)
    is_scheduled = models.BooleanField(default=False, help_text="Whether this report runs on a schedule")
    schedule_frequency = models.CharField(max_length=50, blank=True, null=True, help_text="Frequency for scheduled reports (daily, weekly, monthly)")
    last_run = models.DateTimeField(null=True, blank=True, help_text="When this report was last executed")
    parameters = models.JSONField(default=dict, blank=True)
    file_path = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    report_data = models.TextField(null=True, blank=True, help_text="JSON or serialized data for the report")
    report_file = models.FileField(upload_to='reports/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} ({self.report_type})"

class DatabaseBackup(models.Model):
    """Model for tracking database backup history"""
    backup_id = models.AutoField(primary_key=True)
    backup_file = models.CharField(max_length=255, help_text="Path or identifier of the backup file")
    backup_date = models.DateTimeField(default=timezone.now)
    backup_size = models.IntegerField(default=0, help_text="Size in bytes")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_automatic = models.BooleanField(default=True, help_text="Whether backup was created automatically or manually")
    status = models.CharField(max_length=20, choices=[
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('in_progress', 'In Progress'),
    ], default='success')
    notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-backup_date']
        verbose_name = "Database Backup"
        verbose_name_plural = "Database Backups"
    
    def __str__(self):
        return f"Backup from {self.backup_date.strftime('%Y-%m-%d %H:%M:%S')}"
