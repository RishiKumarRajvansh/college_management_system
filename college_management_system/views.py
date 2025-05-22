from django.shortcuts import render
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta

from student_management.models import Student
from faculty_management.models import Faculty
from course_management.models import Course
from attendance_management.models import Attendance
from examination.models import Examination, Result
from library_management.models import Book, BookIssue
from hostel_management.models import Hostel, Room, HostelAllocation
from fee_management.models import FeeCategory, FeeStructure, Payment
from reporting.models import Report

def home_view(request):
    """View for rendering the home page with necessary context variables"""
    # Get counts from database
    try:
        # Base entity counts
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
        today = timezone.now().date()
        last_week = today - timedelta(days=7)
        recent_book_issues = BookIssue.objects.filter(issue_date__gte=last_week).count()
        recent_room_allocations = HostelAllocation.objects.filter(allocation_date__gte=last_week).count()
        recent_payments = Payment.objects.filter(payment_date__gte=last_week).count()
        
        # Attendance summary
        total_attendance = Attendance.objects.count()
        present_count = Attendance.objects.filter(status='present').count()
        attendance_rate = (present_count / total_attendance * 100) if total_attendance > 0 else 0
    except Exception as e:
        # Provide default values if there's an error
        student_count = 0
        faculty_count = 0
        course_count = 0
        book_count = 0
        borrowed_books = 0
        hostel_count = 0
        room_count = 0
        occupied_rooms = 0
        total_fees_collected = 0
        pending_payments = 0
        recent_book_issues = 0
        recent_room_allocations = 0
        recent_payments = 0
        total_attendance = 0
        attendance_rate = 0
        print(f"Error loading dashboard statistics: {e}")

    context = {
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
    }
    return render(request, 'home.html', context)
