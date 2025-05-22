from django.db import models

class Report(models.Model):
    REPORT_TYPES = (
        ('student', 'Student Report'),
        ('faculty', 'Faculty Report'),
        ('attendance', 'Attendance Report'),
        ('examination', 'Examination Report'),
        ('fee', 'Fee Report'),
        ('library', 'Library Report'),
        ('hostel', 'Hostel Report'),
        ('custom', 'Custom Report'),
    )
    
    report_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    generated_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='generated_reports')
    generation_date = models.DateTimeField(auto_now_add=True)
    parameters = models.JSONField(default=dict)
    file_path = models.CharField(max_length=255, null=True, blank=True)
    is_scheduled = models.BooleanField(default=False)
    schedule_frequency = models.CharField(max_length=50, null=True, blank=True)
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.report_type}) - {self.generation_date}"
