from django.shortcuts import render
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings

from student_management.models import Student
from faculty_management.models import Faculty
from course_management.models import Course
from attendance_management.models import Attendance
from examination.models import Examination, Result
from library_management.models import Book, BookIssue
from hostel_management.models import Hostel, Room, HostelAllocation
from fee_management.models import FeeCategory, FeeStructure, Payment
from reporting.models import Report, Notification
from user_authentication.models import AuditTrail, UserProfile

import django
import platform
import datetime

# Helper function to check if user is admin or superuser
def is_admin(user):
    if not user.is_authenticated:
        return False
    try:
        return (hasattr(user, 'profile') and user.profile.user_type == 'admin') or user.is_superuser
    except UserProfile.DoesNotExist:
        return False

@login_required
def home_view(request):
    """View for rendering the home page with necessary context variables"""
    context = {}
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    try:
        # Get role-based recent activities
        from user_authentication.utils import get_relevant_activities
        recent_activities = get_relevant_activities(request.user, limit=15)
        context['recent_activities'] = recent_activities
        
        # If user is admin or superuser, redirect to admin dashboard
        if is_admin(request.user):
            return admin_dashboard(request)
            
        # If user is authenticated (student/faculty), load appropriate data
        if request.user.is_authenticated:
            # Determine user type from profile if exists
            user_type = None
            try:
                if hasattr(request.user, 'profile'):
                    user_type = request.user.profile.user_type
            except:
                pass
                
            # Student-specific view
            if user_type == 'student':
                try:
                    student = Student.objects.get(user=request.user)
                    context['student'] = student
                    
                    # Get attendance statistics
                    context['attendance'] = Attendance.objects.filter(
                        student=student, 
                        date__gte=today - timedelta(days=30)
                    # Attendance uses attendance_id as its explicit primary key.
                    ).values('status').annotate(count=Count('attendance_id'))
                    
                    # Get exam results
                    context['results'] = Result.objects.filter(student=student).order_by('-created_at')[:5]
                    
                    # Get fee payment status
                    context['payments'] = Payment.objects.filter(student=student).order_by('-payment_date')[:5]
                    
                    # Get borrowed books
                    context['book_issues'] = BookIssue.objects.filter(
                        student=student,
                        is_returned=False
                    # BookIssue stores the expected due date as return_date.
                    ).order_by('return_date')
                    
                    # Get hostel information
                    try:
                        context['hostel_allocation'] = HostelAllocation.objects.get(
                            student=student,
                            is_active=True
                        )
                    except HostelAllocation.DoesNotExist:
                        context['hostel_allocation'] = None
                    
                except Student.DoesNotExist:
                    pass
            
            # Faculty-specific view
            elif user_type == 'faculty':
                try:
                    faculty = Faculty.objects.get(user=request.user)
                    context['faculty'] = faculty
                    
                    # Get courses taught by faculty
                    context['courses'] = Course.objects.filter(faculty=faculty)
                    
                    # Get upcoming exams for faculty's courses
                    context['upcoming_exams'] = Examination.objects.filter(
                        course__in=context['courses'],
                        date__date__gte=today
                    ).order_by('date')[:5]
                    
                    # Get pending result submissions
                    # Treat past examinations with no result rows as pending; the
                    # Examination model has no separate completion flag.
                    context['pending_results'] = Examination.objects.filter(
                        course__in=context['courses'],
                        date__date__lt=today,
                        results__isnull=True,
                    ).distinct().count()
                    
                except Faculty.DoesNotExist:
                    pass
            
            # Get unread notifications for authenticated users
            context['unread_notifications'] = Notification.objects.filter(
                user=request.user,
                read=False
            ).order_by('-created_at')[:5]
    
    except Exception as e:
        # Log the error but don't crash
        print(f"Error in home_view: {e}")
        
    return render(request, 'home.html', context)

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard view showing overview of all system modules"""
    context = {}
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    
    try:
        # Get recent activities
        recent_activities = AuditTrail.objects.all().order_by('-action_time')[:10]
        context['recent_activities'] = recent_activities
        
        # Base entity counts
        context['student_count'] = Student.objects.count()
        context['faculty_count'] = Faculty.objects.count()
        context['course_count'] = Course.objects.count()
        context['report_count'] = Report.objects.count()
        
        # Attendance statistics
        today_attendance = Attendance.objects.filter(date=today)
        context['present_count'] = today_attendance.filter(status='present').count()
        context['absent_count'] = today_attendance.filter(status='absent').count()
        context['late_count'] = today_attendance.filter(status='late').count()
        context['excused_count'] = today_attendance.filter(status='excused').count()
        
        total_attendance = context['present_count'] + context['absent_count'] + context['late_count'] + context['excused_count']
        context['today_attendance_percentage'] = round(context['present_count'] * 100 / total_attendance) if total_attendance > 0 else 0        # Examination statistics
        results = Result.objects.all()
        # Use examination.total_marks instead of trying to aggregate total_marks from Result
        total_marks_possible = 0
        for result in results:
            total_marks_possible += result.examination.total_marks if hasattr(result.examination, 'total_marks') else 100
        
        obtained_marks = results.aggregate(obtained=Sum('marks_obtained'))['obtained'] or 0
        context['average_score'] = round(obtained_marks * 100 / total_marks_possible) if total_marks_possible > 0 else 0
        
        context['upcoming_exam_count'] = Examination.objects.filter(date__date__gte=today).count()
        # Calculate results pending by checking exams in the past that don't have results
        past_exams = Examination.objects.filter(date__date__lt=today)
        results_pending_count = 0
        for exam in past_exams:
            if not Result.objects.filter(examination=exam).exists():
                results_pending_count += 1
        context['results_pending_count'] = results_pending_count
        
        # Library statistics
        context['book_count'] = Book.objects.count()
        context['borrowed_books'] = BookIssue.objects.filter(is_returned=False).count()
        context['recent_book_issues'] = BookIssue.objects.filter(issue_date__gte=last_week).count()
          # Hostel statistics
        context['hostel_count'] = Hostel.objects.count()
        context['room_count'] = Room.objects.count()
        context['occupied_rooms'] = Room.objects.filter(status='occupied').count()
        context['recent_room_allocations'] = HostelAllocation.objects.filter(allocation_date__gte=last_week).count()
        
        # Fee statistics
        context['total_fees_collected'] = Payment.objects.filter(status='completed').aggregate(Sum('amount'))['amount__sum'] or 0
        context['pending_payments'] = Payment.objects.filter(status='pending').count()
        context['recent_payments'] = Payment.objects.filter(payment_date__gte=last_week).count()
        
        # System info for modal
        context['now'] = timezone.now()
        context['app_version'] = '1.0.0'  # Set your app version
        context['django_version'] = django.__version__
        context['database_info'] = 'SQLite' if 'sqlite' in settings.DATABASES['default']['ENGINE'] else 'PostgreSQL'
          # Real system data
        try:
            import psutil
            # Get actual server uptime if on Linux/Unix
            uptime_seconds = psutil.boot_time()
            uptime = timezone.now() - timezone.datetime.fromtimestamp(uptime_seconds, tz=timezone.get_current_timezone())
            days, remainder = divmod(uptime.total_seconds(), 86400)
            hours, remainder = divmod(remainder, 3600)
            context['server_uptime'] = f"{int(days)} days, {int(hours)} hours"
            
            # Get CPU load
            context['system_load'] = round(psutil.cpu_percent(interval=0.1), 1)
        except ImportError:
            # Fallback if psutil not installed
            context['server_uptime'] = 'Unknown (install psutil for real data)'
            context['system_load'] = 'Unknown'
            
        # Get last backup time from database or settings
        try:
            from django.db.models import Max
            from reporting.models import DatabaseBackup
            last_backup = DatabaseBackup.objects.aggregate(latest=Max('backup_date'))['latest']
            if last_backup:
                context['last_backup'] = last_backup.strftime('%Y-%m-%d %H:%M:%S')
            else:
                context['last_backup'] = 'No backups found'
        except:
            context['last_backup'] = 'Unknown'
        
    except Exception as e:
        # Log the error but don't crash
        print(f"Error in admin_dashboard: {e}")
    
    return render(request, 'admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def system_activity_logs(request):
    """Compatibility route for the detailed auth activity log page."""
    from user_authentication.views_activity import system_activity_logs as detailed_activity_logs

    return detailed_activity_logs(request)
