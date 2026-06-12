from django.db.models import Q
from .models import AuditTrail

def get_relevant_activities(user, limit=10):
    """
    Get relevant activities for a user based on their role.
    
    Args:
        user: The user object
        limit: Maximum number of activities to return, or None for all activities
    
    Returns:
        Queryset of relevant AuditTrail objects
    """
    if not user.is_authenticated:
        return AuditTrail.objects.none()

    if user.is_superuser:
        activities = AuditTrail.objects.all().order_by('-action_time')
        return activities[:limit] if limit else activities

    # Get user profile
    profile = getattr(user, 'profile', None)
    if not profile:
        return AuditTrail.objects.filter(user=user).order_by('-action_time')[:limit]
      # Admin sees all activities
    if profile.user_type == 'admin' or user.is_superuser:
        activities = AuditTrail.objects.all().order_by('-action_time')
        return activities[:limit] if limit else activities
    
    # Faculty sees their own activities plus activities related to their courses and students
    elif profile.user_type == 'faculty':
        try:
            faculty = user.faculty_profile
            # Get courses taught by this faculty
            courses = faculty.courses.all()
            course_ids = [course.course_id for course in courses]
            
            # Activities related to faculty
            faculty_activities = AuditTrail.objects.filter(
                Q(user=user) |  # Own activities
                Q(module='course', description__contains=faculty.name) |  # Course-related activities
                Q(module='examination', description__contains=faculty.name) |  # Exam-related activities
                Q(module__in=['course_management', 'examination']) & Q(description__regex=r'course.*(' + '|'.join([str(c) for c in course_ids]) + ')')  # Activities mentioning faculty's courses
            )
            activities = faculty_activities.order_by('-action_time')
            return activities[:limit] if limit else activities
            
        except Exception:
            # Fallback to own activities if faculty profile doesn't exist
            activities = AuditTrail.objects.filter(user=user).order_by('-action_time')
            return activities[:limit] if limit else activities
    
    # Students see their own activities plus activities related to their course
    elif profile.user_type == 'student':
        try:
            student = user.student_profile
            # Get activities related to student's course
            course_id = student.course.course_id if student.course else None
            
            if course_id:
                student_activities = AuditTrail.objects.filter(
                    Q(user=user) |  # Own activities
                    Q(module='attendance', description__contains=f'student {student.student_id}') |  # Attendance
                    Q(module='examination', description__contains=f'student {student.student_id}') |  # Exams
                    Q(module='fee_management', description__contains=f'student {student.student_id}') |  # Fees
                    Q(module='course_management', description__contains=f'course {course_id}')  # Course updates
                )
                activities = student_activities.order_by('-action_time')
                return activities[:limit] if limit else activities
            else:
                # If no course is assigned, just show own activities
                activities = AuditTrail.objects.filter(user=user).order_by('-action_time')
                return activities[:limit] if limit else activities
                
        except Exception:
            # Fallback to own activities
            activities = AuditTrail.objects.filter(user=user).order_by('-action_time')
            return activities[:limit] if limit else activities
    
    # Default: return user's own activities
    activities = AuditTrail.objects.filter(user=user).order_by('-action_time')
    return activities[:limit] if limit else activities
