"""
API views for Course Management module
"""
from django.http import JsonResponse
from django.db.models import Count
from .models import Course
from django.contrib.auth.decorators import login_required

@login_required
def course_credit_distribution(request):
    """API endpoint to return course distribution by credit value"""
    # Group courses by credit value and count them
    credit_distribution = Course.objects.values('credits').annotate(
        count=Count('id')
    ).order_by('credits')
    
    # Create data structure for chart.js
    labels = [f"{item['credits']} Credits" for item in credit_distribution]
    data = [item['count'] for item in credit_distribution]
    
    return JsonResponse({
        'labels': labels,
        'data': data
    })

@login_required
def course_enrollment(request):
    """API endpoint to return top courses by student enrollment"""
    # Get top 5 courses by student count
    top_courses = Course.objects.annotate(
        student_count=Count('student')
    ).order_by('-student_count')[:5]
    
    # Create data structure for chart.js
    labels = [course.name for course in top_courses]
    data = [course.student_count for course in top_courses]
    
    return JsonResponse({
        'labels': labels,
        'data': data
    })
