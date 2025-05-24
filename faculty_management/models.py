from django.db import models
from django.contrib.auth.models import User

class Faculty(models.Model):
    faculty_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100, default='General')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.formatted_id})"
        
    @property
    def formatted_id(self):
        """Return the faculty ID formatted as FA000001, FA000002, etc.
        
        Note: This is for display purposes only. The actual faculty_id field
        remains an integer (AutoField) in the database. This property allows us
        to show faculty IDs in a consistent format throughout the application
        while maintaining database integrity with proper data types.
        """
        return f"FA{self.faculty_id:06d}"
