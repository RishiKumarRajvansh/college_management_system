from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Attendance
from .forms import AttendanceForm, BulkAttendanceForm, AttendanceSearchForm
from student_management.models import Student
from datetime import datetime, timedelta
from user_authentication.models import UserProfile  # Added import

# Helper function to check if user is admin or faculty
def is_admin_or_faculty(user):
    if not user.is_authenticated:
        return False
    try:
        # Check if user has a profile and if its type is 'admin' or 'faculty', or if the user is a superuser
        return (hasattr(user, 'profile') and user.profile.user_type in ['admin', 'faculty']) or user.is_superuser
    except UserProfile.DoesNotExist:  # Catching the specific exception if profile does not exist
        return False

@login_required
def attendance_list(request):
    """View to list all attendance records with search and filter options"""
    attendances = Attendance.objects.all().order_by('-date', 'course')
    form = AttendanceSearchForm(request.GET)
    
    # Apply filters if the form is valid
    if form.is_valid():
        student_filter = form.cleaned_data.get('student')
        course_filter = form.cleaned_data.get('course')
        start_date = form.cleaned_data.get('start_date')
        end_date = form.cleaned_data.get('end_date')
        status_filter = form.cleaned_data.get('status')
        
        if student_filter:
            attendances = attendances.filter(student=student_filter)
        
        if course_filter:
            attendances = attendances.filter(course=course_filter)
            
        if start_date:
            attendances = attendances.filter(date__gte=start_date)
            
        if end_date:
            attendances = attendances.filter(date__lte=end_date)
            
        if status_filter:
            attendances = attendances.filter(status=status_filter)
    
    # Paginate the results
    paginator = Paginator(attendances, 15)  # Show 15 attendance records per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_attendances': attendances.count(),
    }
    
    return render(request, 'attendance_management/attendance_list.html', context)

@login_required
@user_passes_test(is_admin_or_faculty)
def attendance_create(request):
    """View to create a new attendance record"""
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            attendance = form.save()
            messages.success(request, 'Attendance record created successfully!')
            return redirect('attendance_detail', pk=attendance.attendance_id)
    else:
        form = AttendanceForm()
    
    context = {
        'form': form,
        'title': 'Add Attendance Record'
    }
    return render(request, 'attendance_management/attendance_form.html', context)

@login_required
@user_passes_test(is_admin_or_faculty)
def bulk_attendance(request):
    """View to create multiple attendance records at once for a course"""
    if request.method == 'POST':
        form = BulkAttendanceForm(request.POST)
        
        # Handle valid form submission
        if form.is_valid():
            course = form.cleaned_data['course']
            date = form.cleaned_data['date']
            
            # Get all students enrolled in the course
            students = Student.objects.filter(course=course)
            
            # Process attendance for each student
            attendance_count = 0
            for student in students:
                field_name = f'student_{student.student_id}'
                if field_name in form.cleaned_data:
                    status = form.cleaned_data[field_name]
                    
                    # Create or update attendance record
                    attendance, created = Attendance.objects.update_or_create(
                        student=student,
                        course=course,
                        date=date,
                        defaults={'status': status}
                    )
                    attendance_count += 1
            
            messages.success(request, f'{attendance_count} attendance records saved successfully!')
            return redirect('attendance_list')
    else:
        form = BulkAttendanceForm()
    
    context = {
        'form': form,
        'title': 'Bulk Attendance Entry'
    }
    return render(request, 'attendance_management/bulk_attendance_form.html', context)

@login_required
def attendance_detail(request, pk):
    """View to display attendance details"""
    attendance = get_object_or_404(Attendance, attendance_id=pk)
    return render(request, 'attendance_management/attendance_detail.html', {'attendance': attendance})

@login_required
@user_passes_test(is_admin_or_faculty)
def attendance_update(request, pk):
    """View to update attendance information"""
    attendance = get_object_or_404(Attendance, attendance_id=pk)
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            attendance = form.save()
            messages.success(request, 'Attendance record updated successfully!')
            return redirect('attendance_detail', pk=attendance.attendance_id)
    else:
        form = AttendanceForm(instance=attendance)
    
    context = {
        'form': form,
        'title': 'Update Attendance Record'
    }
    return render(request, 'attendance_management/attendance_form.html', context)

@login_required
@user_passes_test(is_admin_or_faculty)
def attendance_delete(request, pk):
    """View to delete an attendance record"""
    attendance = get_object_or_404(Attendance, attendance_id=pk)
    
    if request.method == 'POST':
        attendance.delete()
        messages.success(request, 'Attendance record deleted successfully!')
        return redirect('attendance_list')
        
    return render(request, 'attendance_management/attendance_confirm_delete.html', {'attendance': attendance})

@login_required
def student_attendance(request, student_id):
    """View to display attendance records for a specific student"""
    student = get_object_or_404(Student, student_id=student_id)
    attendances = Attendance.objects.filter(student=student).order_by('-date')
    
    # Calculate attendance statistics
    stats = {}
    for course in student.course.all() if hasattr(student, 'course') and hasattr(student.course, 'all') else [student.course]:
        course_attendances = attendances.filter(course=course)
        total = course_attendances.count()
        present = course_attendances.filter(status='present').count()
        absent = course_attendances.filter(status='absent').count()
        late = course_attendances.filter(status='late').count()
        excused = course_attendances.filter(status='excused').count()

        # Keep division safe for students who do not have attendance records yet.
        stats[course.name] = {
            'total': total,
            'present': present,
            'absent': absent,
            'late': late,
            'excused': excused,
            'present_percentage': round((present / total) * 100, 2) if total else 0,
            'absent_percentage': round((absent / total) * 100, 2) if total else 0,
            'late_percentage': round((late / total) * 100, 2) if total else 0,
            'excused_percentage': round((excused / total) * 100, 2) if total else 0,
        }

    paginator = Paginator(attendances, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'attendance_management/student_attendance.html', {
        'student': student,
        'stats': stats,
        'page_obj': page_obj,
        'total_attendances': attendances.count(),
    })
