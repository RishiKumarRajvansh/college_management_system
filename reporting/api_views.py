# api_views.py - API endpoints for dashboard data
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Sum, Case, When, IntegerField, F
from django.db.models.functions import TruncMonth
from django.utils import timezone
from .models import Notification
import datetime
from dateutil.relativedelta import relativedelta
from calendar import month_name
import json

# Import for export functionality
import csv
import tempfile
from openpyxl import Workbook
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

from student_management.models import Student
from attendance_management.models import Attendance
from examination.models import Examination, Result
from course_management.models import Course
from fee_management.models import Payment

@login_required
def attendance_stats(request):
    """API endpoint for attendance statistics"""
    # Get current date and date from 30 days ago
    today = datetime.date.today()
    thirty_days_ago = today - datetime.timedelta(days=30)
    
    # Get attendance data for the last 30 days
    recent_attendance = Attendance.objects.filter(date__gte=thirty_days_ago, date__lte=today)
    
    # Count attendance by status
    attendance_by_status = recent_attendance.values('status').annotate(count=Count('status'))
    
    # Prepare data
    data = {
        'present_count': 0,
        'absent_count': 0,
        'late_count': 0,
        'excused_count': 0,
    }
    
    # Fill in actual counts
    for item in attendance_by_status:
        status = item['status']
        count = item['count']
        
        if status == 'present':
            data['present_count'] = count
        elif status == 'absent':
            data['absent_count'] = count
        elif status == 'late':
            data['late_count'] = count
        elif status == 'excused':
            data['excused_count'] = count
    
    return JsonResponse(data)

@login_required
def exam_performance(request):
    """API endpoint for examination performance statistics"""
    # Get courses with results
    courses_with_results = Course.objects.filter(examinations__results__isnull=False).distinct()
    
    # For each course, calculate average score and pass rate
    courses = []
    average_scores = []
    pass_rates = []
    
    for course in courses_with_results:
        # Get results for this course's exams
        results = Result.objects.filter(examination__course=course)
        
        if results.exists():
            # Calculate average score (percentage)
            average_percentage = results.aggregate(
                avg_percentage=Avg('percentage')
            )['avg_percentage'] or 0
            
            # Calculate pass rate
            pass_count = results.filter(status='pass').count()
            total_count = results.count()
            pass_rate = (pass_count / total_count * 100) if total_count > 0 else 0
            
            # Add to lists
            courses.append(course.name)
            average_scores.append(round(average_percentage, 1))
            pass_rates.append(round(pass_rate, 1))
    
    return JsonResponse({
        'courses': courses,
        'average_scores': average_scores,
        'pass_rates': pass_rates,
    })

@login_required
def enrollment_stats(request):
    """API endpoint for student enrollment statistics"""
    # Get enrollment trend for the last 6 months
    today = datetime.date.today()
    six_months_ago = today - relativedelta(months=6)
    
    # Group students by month of creation
    students_by_month = (
        Student.objects.filter(created_at__date__gte=six_months_ago)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(count=Count('student_id'))
        .order_by('month')
    )
    
    # Prepare data
    months = []
    enrollment_counts = []
    
    # Fill in missing months with zero enrollments
    month_counts = {item['month'].strftime('%Y-%m'): item['count'] for item in students_by_month}
    
    # Generate all months in the 6 month range
    current_month = six_months_ago.replace(day=1)
    while current_month <= today:
        month_key = current_month.strftime('%Y-%m')
        month_name_str = current_month.strftime('%b %Y')
        
        months.append(month_name_str)
        enrollment_counts.append(month_counts.get(month_key, 0))
        
        current_month += relativedelta(months=1)
    
    return JsonResponse({
        'months': months,
        'enrollment_counts': enrollment_counts,
    })

@login_required
def fee_collection_stats(request):
    """API endpoint for fee collection statistics"""
    # Get fee collection trend for the last 6 months
    today = datetime.date.today()
    six_months_ago = today - relativedelta(months=6)
    
    # Group payments by month
    payments_by_month = (
        Payment.objects.filter(payment_date__gte=six_months_ago)
        .annotate(month=TruncMonth('payment_date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )
    
    # Prepare data
    months = []
    amounts = []
    
    # Fill in missing months with zero amounts
    month_amounts = {item['month'].strftime('%Y-%m'): item['total'] for item in payments_by_month}
    
    # Generate all months in the 6 month range
    current_month = six_months_ago.replace(day=1)
    while current_month <= today:
        month_key = current_month.strftime('%Y-%m')
        month_name_str = current_month.strftime('%b %Y')
        
        months.append(month_name_str)
        amounts.append(float(month_amounts.get(month_key, 0)))
        
        current_month += relativedelta(months=1)
    return JsonResponse({
        'months': months,
        'amounts': amounts,
    })

@login_required
def get_notifications(request):
    """API endpoint to get user notifications"""
    user = request.user
    notifications = Notification.objects.filter(user=user).order_by('-created_at')[:10]
    
    notification_list = []
    for notification in notifications:
        notification_list.append({
            'id': notification.id,
            'message': notification.message,
            'type': notification.notification_type,
            'link': notification.link,
            'created_at': notification.created_at.strftime('%b %d, %Y %H:%M'),
            'read': notification.read,
        })
    
    unread_count = Notification.objects.filter(user=user, read=False).count()
    
    return JsonResponse({
        'notifications': notification_list,
        'unread_count': unread_count
    })

@login_required
def mark_notification_read(request, notification_id=None):
    """API endpoint to mark notifications as read"""
    if request.method == 'POST':
        user = request.user
        
        if notification_id:
            # Mark specific notification as read
            try:
                notification = Notification.objects.get(id=notification_id, user=user)
                notification.mark_as_read()
                return JsonResponse({'success': True})
            except Notification.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)
        else:
            # Mark all as read
            notifications = Notification.objects.filter(user=user, read=False)
            for notification in notifications:
                notification.mark_as_read()
            return JsonResponse({'success': True, 'count': notifications.count()})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'}, status=400)

@login_required
def create_notification(request):
    """API endpoint to create notifications (admin only)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
        
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_id = data.get('user_id')
            message = data.get('message')
            notification_type = data.get('type', 'info')
            link = data.get('link', None)
            
            if not user_id or not message:
                return JsonResponse({'success': False, 'error': 'Missing required fields'}, status=400)
                
            from django.contrib.auth.models import User
            try:
                user = User.objects.get(id=user_id)
                notification = Notification.objects.create(
                    user=user,
                    message=message,
                    notification_type=notification_type,
                    link=link
                )
                return JsonResponse({'success': True, 'notification_id': notification.id})
            except User.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'User not found'}, status=404)
                
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)

# Report Export Functionality
@login_required
def export_report(request, report_id):
    """Export report data in various formats"""
    from .models import Report
    
    try:
        report = Report.objects.get(report_id=report_id)
    except Report.DoesNotExist:
        return JsonResponse({'error': 'Report not found'}, status=404)
    
    export_format = request.GET.get('format', 'pdf')
    
    # Get report data based on the report type
    data = _get_report_data(report)
    if not data:
        return JsonResponse({'error': 'No data available for this report'}, status=404)
    
    # Export based on requested format
    if export_format == 'csv':
        return _export_as_csv(report, data)
    elif export_format == 'excel':
        return _export_as_excel(report, data)
    elif export_format == 'pdf':
        return _export_as_pdf(report, data)
    else:
        return JsonResponse({'error': 'Unsupported format'}, status=400)

def _get_report_data(report):
    """Retrieve data for the given report"""
    report_type = report.report_type
    
    if report_type == 'student':
        students = Student.objects.all()
        headers = ['ID', 'Name', 'Email', 'Course', 'Year']
        rows = [[
            s.formatted_id,
            s.name,
            s.email,
            s.course.name,
            s.year,
        ] for s in students]
        return {'headers': headers, 'rows': rows}
    
    elif report_type == 'attendance':
        # Get date range from report parameters or use default
        start_date = report.parameters.get('start_date', (datetime.date.today() - datetime.timedelta(days=30)).isoformat())
        end_date = report.parameters.get('end_date', datetime.date.today().isoformat())
        
        attendances = Attendance.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('student', 'date')
        
        headers = ['Student ID', 'Student Name', 'Date', 'Status']
        rows = [[
            a.student.formatted_id,
            a.student.name,
            a.date.strftime('%Y-%m-%d'),
            a.status.capitalize()
        ] for a in attendances]
        return {'headers': headers, 'rows': rows}
    
    elif report_type == 'examination':
        results = Result.objects.all().order_by('student', 'examination')
        
        headers = ['Student ID', 'Student Name', 'Exam', 'Course', 'Score', 'Percentage', 'Status']
        rows = [[
            r.student.formatted_id,
            r.student.name,
            r.examination.exam_name,
            r.examination.course.name,
            r.marks_obtained,
            r.percentage,
            r.status.capitalize()
        ] for r in results]
        return {'headers': headers, 'rows': rows}
    
    elif report_type == 'fee':
        payments = Payment.objects.all().order_by('student', '-payment_date')
        
        headers = ['Receipt No', 'Student ID', 'Student Name', 'Amount', 'Payment Date', 'Payment Method']
        rows = [[
            p.receipt_number,
            p.student.formatted_id,
            p.student.name,
            p.amount,
            p.payment_date.strftime('%Y-%m-%d'),
            p.payment_method.capitalize()
        ] for p in payments]
        return {'headers': headers, 'rows': rows}
    
    # Add more report types as needed
    
    return None

def _export_as_csv(report, data):
    """Export report data as CSV file"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report.report_type}_report_{datetime.date.today().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(data['headers'])
    writer.writerows(data['rows'])
    
    return response

def _export_as_excel(report, data):
    """Export report data as Excel file"""
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{report.report_type}_report_{datetime.date.today().strftime("%Y%m%d")}.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = report.report_type.capitalize()[:31]

    # openpyxl is already a project dependency and avoids the missing xlwt import.
    ws.append(data['headers'])
    for row_data in data['rows']:
        ws.append([str(cell_value) for cell_value in row_data])

    wb.save(response)
    return response

def _export_as_pdf(report, data):
    """Export report data as PDF file"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{report.report_type}_report_{datetime.date.today().strftime("%Y%m%d")}.pdf"'
    
    # Create a PDF document
    doc = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    
    # Add title
    title = f"{report.report_type.capitalize()} Report"
    elements.append(Table([[title]], colWidths=[500], rowHeights=[30]))
    elements.append(Table([['Generated on: ' + datetime.date.today().strftime("%Y-%m-%d")]], colWidths=[500], rowHeights=[20]))
    
    # Convert data to table format
    table_data = [data['headers']] + data['rows']
    
    # Create the table
    table = Table(table_data)
    
    # Style the table
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    
    table.setStyle(style)
    elements.append(table)
    
    # Build the PDF
    doc.build(elements)
    
    return response
