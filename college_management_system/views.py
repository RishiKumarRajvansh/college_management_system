from django.shortcuts import render
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

from student_management.models import Student
from faculty_management.models import Faculty
from course_management.models import Course
from attendance_management.models import Attendance
from examination.models import Examination, Result
from library_management.models import Book, BookIssue
from hostel_management.models import Hostel, Room, HostelAllocation
from fee_management.models import FeeCategory, FeeStructure, Payment
from reporting.models import Report
from user_authentication.models import AuditTrail

def home_view(request):
    """View for rendering the home page with necessary context variables"""
    context = {}
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    
    try:
        # Get recent activities for all users
        recent_activities = AuditTrail.objects.all().order_by('-action_time')[:10]
        context['recent_activities'] = recent_activities
        
        # Base entity counts for admin dashboard
        student_count = Student.objects.count()
        faculty_count = Faculty.objects.count()
        course_count = Course.objects.count()
        
        # Library statistics
        book_count = Book.objects.count()
        borrowed_books = BookIssue.objects.filter(is_returned=False).count()
        
        # Hostel statistics
        hostel_count = Hostel.objects.count()
        room_count = Room.objects.count()
        occupied_rooms = Room.objects.filter(status='occupied').count()
        
        # Fee statistics
        total_fees_collected = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        pending_payments = Payment.objects.filter(status='pending').count()
        
        # Recent activity
        recent_book_issues = BookIssue.objects.filter(issue_date__gte=last_week).count()
        recent_room_allocations = HostelAllocation.objects.filter(allocation_date__gte=last_week).count()
        recent_payments = Payment.objects.filter(payment_date__gte=last_week).count()
        
        # Attendance summary
        total_attendance = Attendance.objects.count()
        present_count = Attendance.objects.filter(status='present').count()
        attendance_rate = (present_count / total_attendance * 100) if total_attendance > 0 else 0
        
        # Populate context with admin statistics
        context.update({
            'student_count': student_count,
            'faculty_count': faculty_count,
            'course_count': course_count,
            'book_count': book_count,
            'borrowed_books': borrowed_books,
            'hostel_count': hostel_count,
            'room_count': room_count,
            'occupied_rooms': occupied_rooms,
            'available_rooms': room_count - occupied_rooms,
            'total_fees_collected': total_fees_collected,
            'pending_payments': pending_payments,
            'recent_book_issues': recent_book_issues,
            'recent_room_allocations': recent_room_allocations,
            'recent_payments': recent_payments,
            'total_attendance': total_attendance,
            'attendance_rate': round(attendance_rate, 1),
        })
        
        # Get upcoming exams for all users
        upcoming_exams = Examination.objects.filter(date__gte=today).order_by('date')[:5]
        context['upcoming_exams'] = upcoming_exams
        
        # Student-specific dashboard data
        if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.user_type == 'student':
            try:
                # Get student record for the current user
                student = Student.objects.get(user=request.user)
                
                # Calculate student's attendance percentage
                student_attendances = Attendance.objects.filter(student=student)
                total_student_classes = student_attendances.count()
                present_classes = student_attendances.filter(status='present').count()
                attendance_percentage = (present_classes / total_student_classes * 100) if total_student_classes > 0 else 0
                context['attendance_percentage'] = round(attendance_percentage, 1)
                
                # Count upcoming exams for student's course
                upcoming_exams_count = Examination.objects.filter(
                    date__gte=today,
                    course=student.course
                ).count()
                context['upcoming_exams_count'] = upcoming_exams_count
                
                # Calculate pending fees for student
                pending_fees = Payment.objects.filter(
                    student=student,
                    status='pending'
                ).aggregate(Sum('amount'))['amount__sum'] or 0
                context['pending_fees'] = pending_fees
                
                # Get upcoming due fees
                due_fees = FeeStructure.objects.filter(
                    course=student.course,
                    due_date__gte=today
                ).order_by('due_date')[:5]
                context['due_fees'] = due_fees
                
            except Student.DoesNotExist:
                # Handle case where user profile exists but student record doesn't
                context['attendance_percentage'] = 0
                context['upcoming_exams_count'] = 0
                context['pending_fees'] = 0
                context['due_fees'] = []
        
        # Faculty-specific dashboard data
        elif request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.user_type == 'faculty':
            try:
                # Get faculty record for the current user
                faculty = Faculty.objects.get(user=request.user)
                
                # Count courses taught by this faculty
                faculty_courses = Course.objects.filter(faculty=faculty)
                faculty_courses_count = faculty_courses.count()
                context['faculty_courses_count'] = faculty_courses_count
                
                # Count today's attendance entries by this faculty
                attendance_today_count = Attendance.objects.filter(
                    course__in=faculty_courses,
                    date=today
                ).count()
                context['attendance_today_count'] = attendance_today_count
                
                # Count exams created by this faculty (via their courses)
                faculty_exams_count = Examination.objects.filter(
                    course__in=faculty_courses
                ).count()
                context['faculty_exams_count'] = faculty_exams_count
                
            except Faculty.DoesNotExist:
                # Handle case where user profile exists but faculty record doesn't
                context['faculty_courses_count'] = 0
                context['attendance_today_count'] = 0
                context['faculty_exams_count'] = 0
        
    except Exception as e:
        # Log the error but continue rendering the page with default values
        print(f"Error loading dashboard statistics: {e}")
        
    return render(request, 'home.html', context)
