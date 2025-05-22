from django.db import models

class Course(models.Model):
    course_id = models.AutoField(primary_key=True)
    course_name = models.CharField(max_length=100, unique=True)
    faculty = models.ForeignKey('faculty_management.Faculty', on_delete=models.CASCADE, related_name='courses')
    description = models.TextField(blank=True, null=True)
    credits = models.IntegerField(default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.course_name
