from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, FileResponse, JsonResponse
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
import csv
import io
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from openpyxl import Workbook

from .models import Report, Notification
from .forms import (
    ReportForm, StudentReportForm, FacultyReportForm, AttendanceReportForm, 
    ExaminationReportForm, FeeReportForm, LibraryReportForm, HostelReportForm, 
    ReportSearchForm
)
from student_management.models import Student
from faculty_management.models import Faculty
from course_management.models import Course
from attendance_management.models import Attendance
from examination.models import Examination as Exam, Result as ExamResult
from fee_management.models import FeeCategory, FeeStructure, Payment as FeePayment
from library_management.models import Book, BookIssue
from hostel_management.models import Hostel, Room, HostelAllocation

@login_required
def dashboard(request):
    """Dashboard view for the reporting module"""    # Count reports by type
    report_counts = Report.objects.values('report_type').annotate(count=Count('report_id'))
    report_types_dict = dict(Report.REPORT_TYPES)
    
    # Format the report counts for the chart (for reference on the server side)
    report_types = []
    report_counts_values = []
    
    for item in report_counts:
        report_type = report_types_dict.get(item['report_type'], item['report_type'])
        report_types.append(report_type)
        report_counts_values.append(item['count'])    # Get recent reports
    recent_reports = Report.objects.all().order_by('-generation_date')[:5]
    
    # Get scheduled reports
    scheduled_reports = Report.objects.filter(is_scheduled=True).order_by('last_run')[:5]
    
    # Get system-wide statistics for the dashboard
    total_students = Student.objects.count()
    total_faculty = Faculty.objects.count()
    total_courses = Course.objects.count()
      # Get unread notifications count for the current user
    unread_notifications_count = Notification.objects.filter(
        user=request.user,
        read=False
    ).count()
    
    # Get latest notifications for the dashboard
    latest_notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]
    
    context = {
        'report_counts': report_counts,
        'recent_reports': recent_reports,
        'scheduled_reports': scheduled_reports,
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_courses': total_courses,
        'unread_notifications_count': unread_notifications_count,
        'latest_notifications': latest_notifications,
    }
    
    return render(request, 'reporting/dashboard.html', context)

class ReportListView(LoginRequiredMixin, ListView):
    model = Report
    template_name = 'reporting/report_list.html'
    context_object_name = 'reports'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Report.objects.all().order_by('-generation_date')
        form = ReportSearchForm(self.request.GET)
        
        if form.is_valid():
            title = form.cleaned_data.get('title')
            report_type = form.cleaned_data.get('report_type')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            is_scheduled = form.cleaned_data.get('is_scheduled')
            
            if title:
                queryset = queryset.filter(title__icontains=title)
            
            if report_type:
                queryset = queryset.filter(report_type=report_type)
            
            if start_date:
                queryset = queryset.filter(generation_date__gte=start_date)
                
            if end_date:
                # Add one day to include the end date
                end_date = end_date + timedelta(days=1)
                queryset = queryset.filter(generation_date__lt=end_date)
                
            if is_scheduled:
                is_scheduled_bool = is_scheduled == 'True'
                queryset = queryset.filter(is_scheduled=is_scheduled_bool)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ReportSearchForm(self.request.GET)
        return context

class ReportDetailView(LoginRequiredMixin, DetailView):
    model = Report
    template_name = 'reporting/report_detail.html'
    context_object_name = 'report'
    pk_url_kwarg = 'report_id'

class ReportDeleteView(LoginRequiredMixin, DeleteView):
    model = Report
    template_name = 'reporting/report_confirm_delete.html'
    success_url = reverse_lazy('report_list')
    pk_url_kwarg = 'report_id'

@login_required
def generate_report_options(request):
    """View to select report type"""
    return render(request, 'reporting/generate_report_options.html')

@login_required
def student_report(request):
    """Generate student reports"""
    if request.method == 'POST':
        form = StudentReportForm(request.POST)
        if form.is_valid():
            # Extract form data
            title = form.cleaned_data['report_title']
            description = form.cleaned_data.get('report_description')
            course = form.cleaned_data.get('course')
            year = form.cleaned_data.get('year')
            report_format = form.cleaned_data.get('export_format')
            
            # Query the students based on filters
            students = Student.objects.all()
            
            if course:
                students = students.filter(course=course)
                
            if year and year != '0':
                students = students.filter(year=year)
                
            # Store parameters for the report
            parameters = {
                'course': course.course_id if course else None,
                'year': year,
                'format': report_format
            }
            
            # Create a new report record
            report = Report.objects.create(
                title=title,
                description=description or f"Student report for {course.name if course else 'all courses'}, Year: {year if year and year != '0' else 'All'}",
                report_type='student',
                generated_by=request.user,
                parameters=parameters
            )
            
            if report_format == 'pdf':
                # Generate PDF
                buffer = io.BytesIO()
                p = canvas.Canvas(buffer)
                
                # Add title
                p.setFont("Helvetica-Bold", 16)
                p.drawString(100, 750, title)
                
                # Add report info
                p.setFont("Helvetica", 12)
                p.drawString(100, 730, f"Generated on: {timezone.now().strftime('%B %d, %Y')}")
                p.drawString(100, 710, f"Course: {course.name if course else 'All Courses'}")
                p.drawString(100, 690, f"Year: {year if year and year != '0' else 'All'}")
                p.drawString(100, 670, f"Total Students: {students.count()}")
                
                # Draw table header
                p.setFont("Helvetica-Bold", 10)
                p.drawString(100, 630, "Student ID")
                p.drawString(180, 630, "Name")
                p.drawString(350, 630, "Email")
                p.drawString(450, 630, "Course")
                p.drawString(500, 630, "Year")
                
                # Draw line under header
                p.line(100, 620, 550, 620)
                
                # Draw student data
                y = 600
                p.setFont("Helvetica", 10)
                for student in students:
                    if y < 50:  # Start a new page if we're near the bottom
                        p.showPage()
                        p.setFont("Helvetica", 10)
                        y = 750
                    
                    p.drawString(100, y, str(student.student_id))
                    p.drawString(180, y, student.name)
                    p.drawString(350, y, student.email)
                    p.drawString(450, y, student.course.name)
                    p.drawString(500, y, str(student.year))
                    
                    y -= 20
                
                p.showPage()
                p.save()
                buffer.seek(0)
                
                # Save the PDF to a file
                file_path = f"student_report_{report.report_id}.pdf"
                with open(file_path, 'wb') as f:
                    f.write(buffer.getvalue())
                
                # Update the report with the file path
                report.file_path = file_path
                report.save()
                
                # Serve the PDF
                return FileResponse(buffer, as_attachment=True, filename=f'student_report_{timezone.now().strftime("%Y%m%d")}.pdf')
            
            elif report_format == 'excel':
                workbook = Workbook()
                worksheet = workbook.active
                worksheet.title = 'Students'
                worksheet.append(['Student ID', 'Name', 'Email', 'Course', 'Year', 'Created On'])
                for student in students:
                    worksheet.append([
                        student.formatted_id,
                        student.name,
                        student.email,
                        student.course.name,
                        student.year,
                        student.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    ])

                file_path = f"student_report_{report.report_id}.xlsx"
                workbook.save(file_path)
                
                # Update the report with the file path
                report.file_path = file_path
                report.save()
                
                # Return the file
                with open(file_path, 'rb') as f:
                    response = HttpResponse(f.read(), content_type='application/vnd.ms-excel')
                    response['Content-Disposition'] = f'attachment; filename="student_report_{timezone.now().strftime("%Y%m%d")}.xlsx"'
                    return response
            elif report_format == 'csv':
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="student_report_{timezone.now().strftime("%Y%m%d")}.csv"'
                writer = csv.writer(response)
                writer.writerow(['Student ID', 'Name', 'Email', 'Course', 'Year'])
                for student in students:
                    writer.writerow([student.formatted_id, student.name, student.email, student.course.name, student.year])
                return response
            
            # Redirect to the report detail page
            return redirect('report_detail', report_id=report.report_id)
    else:
        form = StudentReportForm(initial={'report_title': f'Student Report - {timezone.now().strftime("%B %Y")}'})
    
    return render(request, 'reporting/student_report_form.html', {'form': form})

@login_required
def faculty_report(request):
    """Generate faculty reports"""
    if request.method == 'POST':
        form = FacultyReportForm(request.POST)
        if form.is_valid():
            # Extract data and generate faculty report
            title = form.cleaned_data.get('title') or f'Faculty Report - {timezone.now().strftime("%B %Y")}'
            department = form.cleaned_data.get('department')
            report_format = form.cleaned_data.get('format')
            experience = form.cleaned_data.get('experience')
            report_type = form.cleaned_data.get('report_type')
            
            # Query faculty based on filters
            faculty = Faculty.objects.all()
            
            if department:
                faculty = faculty.filter(department=department)
            
            # Create report object
            parameters = {
                'department': department,
                'experience': experience,
                'report_type': report_type,
                'format': report_format
            }
            
            report = Report.objects.create(
                title=title,
                description=f"Faculty report for department: {department if department else 'All'}",
                report_type='faculty',
                generated_by=request.user,
                parameters=parameters
            )
            
            # Generate report file based on format
            # (Similar structure to student report)
            return redirect('report_detail', report_id=report.report_id)
    else:
        form = FacultyReportForm()
    
    return render(request, 'reporting/faculty_report_form.html', {'form': form})

# Additional report views for other modules
@login_required
def fee_report(request):
    """Generate fee reports"""
    if request.method == 'POST':
        form = FeeReportForm(request.POST)
        if form.is_valid():
            # Extract data and generate fee report
            title = form.cleaned_data.get('title') or f'Fee Report - {timezone.now().strftime("%B %Y")}'
            course = form.cleaned_data.get('course')
            student = form.cleaned_data.get('student')
            fee_category = form.cleaned_data.get('category')
            start_date = form.cleaned_data.get('start_date')
            end_date = form.cleaned_data.get('end_date')
            payment_status = form.cleaned_data.get('payment_status')
            report_format = form.cleaned_data.get('format')
            
            # Query fee payments based on filters
            payments = FeePayment.objects.all()

            if course:
                payments = payments.filter(fee_structure__course=course)

            if student:
                payments = payments.filter(student=student)

            if fee_category:
                payments = payments.filter(fee_structure__category=fee_category)
            
            if start_date:
                payments = payments.filter(payment_date__gte=start_date)
                
            if end_date:
                payments = payments.filter(payment_date__lte=end_date)
                
            if payment_status:
                payments = payments.filter(status=payment_status)
            
            # Create report object
            parameters = {
                'course': course.course_id if course else None,
                'student': student.student_id if student else None,
                'fee_category': fee_category.fee_category_id if fee_category else None,
                'start_date': start_date.strftime('%Y-%m-%d') if start_date else None,
                'end_date': end_date.strftime('%Y-%m-%d') if end_date else None,
                'payment_status': payment_status,
                'format': report_format
            }
            
            report = Report.objects.create(
                title=title,
                description=f"Fee report from {start_date or 'beginning'} to {end_date or 'present'}",
                report_type='fee',
                generated_by=request.user,
                parameters=parameters
            )
            
            # Generate report file based on format
            # Implementation would be similar to student report
            return redirect('report_detail', report_id=report.report_id)
    else:
        form = FeeReportForm(initial={
            'title': f'Fee Report - {timezone.now().strftime("%B %Y")}',
            'start_date': (timezone.now() - timedelta(days=30)).date(),
            'end_date': timezone.now().date()
        })
    
    return render(request, 'reporting/fee_report_form.html', {'form': form})

@login_required
def library_report(request):
    """Generate library reports"""
    if request.method == 'POST':
        form = LibraryReportForm(request.POST)
        if form.is_valid():
            report = Report.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data.get('description'),
                report_type='library',
                generated_by=request.user,
                parameters={
                    'book_status': form.cleaned_data.get('book_status'),
                    'date_range': form.cleaned_data.get('date_range'),
                    'start_date': form.cleaned_data.get('start_date').isoformat() if form.cleaned_data.get('start_date') else None,
                    'end_date': form.cleaned_data.get('end_date').isoformat() if form.cleaned_data.get('end_date') else None,
                    'format': form.cleaned_data.get('format'),
                }
            )
            return redirect('report_detail', report_id=report.report_id)
    else:
        form = LibraryReportForm(initial={
            'title': f'Library Report - {timezone.now().strftime("%B %Y")}',
            'start_date': (timezone.now() - timedelta(days=30)).date(),
            'end_date': timezone.now().date()
        })
    
    return render(request, 'reporting/library_report_form.html', {'form': form})

@login_required
def hostel_report(request):
    """Generate hostel reports"""
    if request.method == 'POST':
        form = HostelReportForm(request.POST)
        if form.is_valid():
            report = Report.objects.create(
                title=form.cleaned_data['title'],
                description=form.cleaned_data.get('description'),
                report_type='hostel',
                generated_by=request.user,
                parameters={
                    'hostel': form.cleaned_data.get('hostel').hostel_id if form.cleaned_data.get('hostel') else None,
                    'room_status': form.cleaned_data.get('room_status'),
                    'allocation_status': form.cleaned_data.get('allocation_status'),
                    'date_range': form.cleaned_data.get('date_range'),
                    'start_date': form.cleaned_data.get('start_date').isoformat() if form.cleaned_data.get('start_date') else None,
                    'end_date': form.cleaned_data.get('end_date').isoformat() if form.cleaned_data.get('end_date') else None,
                    'format': form.cleaned_data.get('format'),
                }
            )
            return redirect('report_detail', report_id=report.report_id)
    else:
        form = HostelReportForm(initial={
            'title': f'Hostel Report - {timezone.now().strftime("%B %Y")}',
        })
    
    return render(request, 'reporting/hostel_report_form.html', {'form': form})

@login_required
def attendance_report(request):
    """Generate attendance reports"""
    if request.method == 'POST':
        form = AttendanceReportForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data.get('course')
            student = form.cleaned_data.get('student')
            report = Report.objects.create(
                title=form.cleaned_data.get('title') or f'Attendance Report - {timezone.now().strftime("%B %Y")}',
                description='Attendance report',
                report_type='attendance',
                generated_by=request.user,
                parameters={
                    'course': course.course_id if course else None,
                    'student': student.student_id if student else None,
                    'start_date': form.cleaned_data.get('start_date').isoformat(),
                    'end_date': form.cleaned_data.get('end_date').isoformat(),
                    'report_type': form.cleaned_data.get('report_type'),
                    'format': form.cleaned_data.get('format'),
                }
            )
            return redirect('report_detail', report_id=report.report_id)
    else:
        form = AttendanceReportForm(initial={
            'title': f'Attendance Report - {timezone.now().strftime("%B %Y")}',
            'start_date': (timezone.now() - timedelta(days=30)).date(),
            'end_date': timezone.now().date()
        })
    
    return render(request, 'reporting/attendance_report_form.html', {'form': form})

@login_required
def examination_report(request):
    """Generate examination reports"""
    if request.method == 'POST':
        form = ExaminationReportForm(request.POST)
        if form.is_valid():
            course = form.cleaned_data.get('course')
            examination = form.cleaned_data.get('examination')
            report = Report.objects.create(
                title=form.cleaned_data.get('title') or f'Examination Report - {timezone.now().strftime("%B %Y")}',
                description='Examination report',
                report_type='examination',
                generated_by=request.user,
                parameters={
                    'course': course.course_id if course else None,
                    'examination': examination.exam_id if examination else None,
                    'exam_type': form.cleaned_data.get('exam_type'),
                    'status': form.cleaned_data.get('status'),
                    'start_date': form.cleaned_data.get('start_date').isoformat() if form.cleaned_data.get('start_date') else None,
                    'end_date': form.cleaned_data.get('end_date').isoformat() if form.cleaned_data.get('end_date') else None,
                    'format': form.cleaned_data.get('format'),
                }
            )
            return redirect('report_detail', report_id=report.report_id)
    else:
        form = ExaminationReportForm(initial={
            'title': f'Examination Report - {timezone.now().strftime("%B %Y")}'
        })
    
    return render(request, 'reporting/examination_report_form.html', {'form': form})
