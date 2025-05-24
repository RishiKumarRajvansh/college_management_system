from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    student_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    course = models.ForeignKey('course_management.Course', on_delete=models.CASCADE)
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.formatted_id})"

    @property
    def formatted_id(self):
        """Return the student ID formatted as ST000001, ST000002, etc.
        
        Note: This is for display purposes only. The actual student_id field
        remains an integer (AutoField) in the database. This property allows us
        to show student IDs in a consistent format throughout the application
        while maintaining database integrity with proper data types.
        """
        return f"ST{self.student_id:06d}"
