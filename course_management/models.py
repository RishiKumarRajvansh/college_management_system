from django.db import models

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=20, unique=True, default='TMP001')
    name = models.CharField(max_length=100, default='Temporary Course')
    faculty = models.ForeignKey('faculty_management.Faculty', on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    credits = models.IntegerField(default=3)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code}: {self.name}"
        
    class Meta:
        ordering = ['code', 'name']
