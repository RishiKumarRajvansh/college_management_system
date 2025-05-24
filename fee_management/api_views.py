from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Payment, FeeCategory, FeeStructure
from student_management.models import Student
from course_management.models import Course

def fee_dashboard_data(request):
    """API endpoint for fee management dashboard data"""
    try:
        # Payment status distribution
        payment_status_data = []
        
        for status, label in Payment.PAYMENT_STATUS:
            count = Payment.objects.filter(status=status).count()
            payment_status_data.append({'status': label, 'count': count})        # Monthly payment collection (last 12 months)
        monthly_collection = []
        today = timezone.now().date()
        
        for i in range(12):
            month_start = today.replace(day=1) - timedelta(days=30*i)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            total = Payment.objects.filter(
                payment_date__range=[month_start, month_end],
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
                
            monthly_collection.append({
                'month': month_start.strftime('%b %Y'),
                'amount': float(total)
            })
        
        monthly_collection.reverse()  # Show oldest to newest        # Payment method distribution
        payment_method_data = []
        
        for method, label in Payment.PAYMENT_METHODS:
            count = Payment.objects.filter(payment_method=method).count()
            payment_method_data.append({'method': label, 'count': count})
              # Fee category collection
        category_collection = []
        categories = FeeCategory.objects.all()
        
        for category in categories:
            total = Payment.objects.filter(
                fee_structure__category=category,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            category_collection.append({
                'category': category.name,
                'amount': float(total)
            })
        
        # Course-wise fee collection
        course_collection = []
        courses = Course.objects.all()[:10]  # Top 10 courses
        for course in courses:
            total = Payment.objects.filter(
                fee_structure__course=course,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            course_collection.append({
                'course': course.name,
                'amount': float(total)
            })
        
        # Recent payment trends (last 30 days)
        recent_trends = []
        for i in range(30):
            date = today - timedelta(days=i)
            count = Payment.objects.filter(payment_date=date).count()
            recent_trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'count': count
            })
        
        recent_trends.reverse()
        
        return JsonResponse({
            'success': True,
            'data': {
                'payment_status': payment_status_data,
                'monthly_collection': monthly_collection,
                'payment_methods': payment_method_data,
                'category_collection': category_collection,
                'course_collection': course_collection,
                'recent_trends': recent_trends
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def fee_statistics(request):
    """API endpoint for fee statistics"""
    try:
        # Basic statistics
        total_collected = Payment.objects.filter(status='completed').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        pending_amount = Payment.objects.filter(status='pending').aggregate(
            total=Sum('amount')
        )['total'] or 0
        
        total_students = Student.objects.count()
        students_with_pending = Payment.objects.filter(status='pending').values('student').distinct().count()
        
        # Defaulter statistics
        overdue_payments = Payment.objects.filter(
            status='pending',
            fee_structure__due_date__lt=timezone.now().date()
        ).count()
        
        return JsonResponse({
            'success': True,
            'statistics': {
                'total_collected': float(total_collected),
                'pending_amount': float(pending_amount),
                'collection_rate': round((float(total_collected) / (float(total_collected) + float(pending_amount)) * 100), 2) if (total_collected + pending_amount) > 0 else 0,
                'total_students': total_students,
                'students_with_pending': students_with_pending,
                'overdue_payments': overdue_payments,
                'payment_compliance': round(((total_students - students_with_pending) / total_students * 100), 2) if total_students > 0 else 100
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)