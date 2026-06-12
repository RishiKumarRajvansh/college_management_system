from django.db import models

class Examination(models.Model):
    EXAM_TYPES = (
        ('midterm', 'Mid Term'),
        ('final', 'Final Exam'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('project', 'Project'),
        ('other', 'Other'),
    )
    
    exam_id = models.AutoField(primary_key=True)
    course = models.ForeignKey('course_management.Course', on_delete=models.CASCADE, related_name='examinations')
    exam_name = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPES)
    date = models.DateTimeField()
    duration = models.IntegerField(help_text='Duration in minutes', default=60)
    total_marks = models.DecimalField(max_digits=5, decimal_places=2)
    passing_marks = models.DecimalField(max_digits=5, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.exam_name} - {self.course.name}"

class Result(models.Model):
    GRADE_CHOICES = (
        ('A+', 'A+'), ('A', 'A'), ('B+', 'B+'), ('B', 'B'), 
        ('C+', 'C+'), ('C', 'C'), ('D', 'D'), ('F', 'F')
    )
    
    STATUS_CHOICES = (
        ('pass', 'Pass'),
        ('fail', 'Fail'),
        ('absent', 'Absent'),
        ('incomplete', 'Incomplete'),
    )
    
    result_id = models.AutoField(primary_key=True)
    student = models.ForeignKey('student_management.Student', on_delete=models.CASCADE, related_name='results')
    examination = models.ForeignKey(Examination, on_delete=models.CASCADE, related_name='results')
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES, blank=True, null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='incomplete')
    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'examination']
        
    def __str__(self):
        return f"{self.student.name} - {self.examination.exam_name} - {self.marks_obtained}"
        
    def save(self, *args, **kwargs):
        # Calculate percentage
        if self.marks_obtained and self.examination.total_marks:
            self.percentage = (self.marks_obtained / self.examination.total_marks) * 100
            
            # Determine status
            if self.marks_obtained >= self.examination.passing_marks:
                self.status = 'pass'
            else:
                self.status = 'fail'
                
            # Assign grade based on percentage
            if self.percentage >= 90:
                self.grade = 'A+'
            elif self.percentage >= 80:
                self.grade = 'A'
            elif self.percentage >= 70:
                self.grade = 'B+'
            elif self.percentage >= 60:
                self.grade = 'B'
            elif self.percentage >= 50:
                self.grade = 'C+'
            elif self.percentage >= 40:
                self.grade = 'C'
            elif self.percentage >= 33:
                self.grade = 'D'
            else:
                self.grade = 'F'
                
        super().save(*args, **kwargs)
