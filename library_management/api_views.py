from django.http import JsonResponse
from django.db.models import Count, Sum, Q, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from .models import Book, BookIssue
from student_management.models import Student

def library_dashboard_data(request):
    """API endpoint for library management dashboard data"""
    try:
        # Book availability status
        availability_data = [
            {'status': 'Available', 'count': Book.objects.filter(availability=True).count()},
            {'status': 'Issued', 'count': Book.objects.filter(availability=False).count()}
        ]
        
        # Monthly book issues (last 12 months)
        monthly_issues = []
        today = timezone.now().date()
        for i in range(12):
            month_start = today.replace(day=1) - timedelta(days=30*i)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            count = BookIssue.objects.filter(
                issue_date__range=[month_start, month_end]
            ).count()
            
            monthly_issues.append({
                'month': month_start.strftime('%b %Y'),
                'issues': count
            })
        
        monthly_issues.reverse()
        
        # Popular books (most issued)
        popular_books = []
        books_with_issues = Book.objects.annotate(
            issue_count=Count('issues')
        ).filter(issue_count__gt=0).order_by('-issue_count')[:10]
        
        for book in books_with_issues:
            popular_books.append({
                'title': book.title,
                'author': book.author,
                'issues': book.issue_count
            })
        
        # Overdue books
        overdue_books = []
        today = timezone.now().date()
        overdue_issues = BookIssue.objects.filter(
            return_date__lt=today,
            is_returned=False
        ).select_related('book', 'student')[:10]
        
        for issue in overdue_issues:
            days_overdue = (today - issue.return_date).days
            overdue_books.append({
                'book_title': issue.book.title,
                'student_name': issue.student.name,
                'days_overdue': days_overdue,
                'fine_amount': float(issue.fine_amount)
            })
        
        # Issue trends (last 30 days)
        issue_trends = []
        for i in range(30):
            date = today - timedelta(days=i)
            issues = BookIssue.objects.filter(issue_date=date).count()
            returns = BookIssue.objects.filter(actual_return_date=date).count()
            issue_trends.append({
                'date': date.strftime('%Y-%m-%d'),
                'issues': issues,
                'returns': returns
            })
        
        issue_trends.reverse()
        
        # Genre/Category distribution (based on book titles - simple categorization)
        genre_data = []        # Get actual book categories/genres from titles and publications
        total_books = Book.objects.count()
        
        # Extract genres from books using categories or keywords in titles
        genres = ['Fiction', 'Science', 'Technology', 'History', 'Mathematics', 'Literature']
        for genre in genres:
            count = Book.objects.filter(
                Q(title__icontains=genre.lower()) | 
                Q(publication__icontains=genre.lower())
            ).count()
            if count > 0:
                genre_data.append({'genre': genre, 'count': count})
        
        return JsonResponse({
            'success': True,
            'data': {
                'availability': availability_data,
                'monthly_issues': monthly_issues,
                'popular_books': popular_books,
                'overdue_books': overdue_books,
                'issue_trends': issue_trends,
                'genre_distribution': genre_data
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

def library_statistics(request):
    """API endpoint for library statistics"""
    try:
        # Basic statistics
        total_books = Book.objects.count()
        available_books = Book.objects.filter(availability=True).count()
        issued_books = Book.objects.filter(availability=False).count()
        
        # Issue statistics
        total_issues = BookIssue.objects.count()
        active_issues = BookIssue.objects.filter(is_returned=False).count()
        overdue_count = BookIssue.objects.filter(
            return_date__lt=timezone.now().date(),
            is_returned=False
        ).count()
        
        # Fine statistics
        total_fines = BookIssue.objects.aggregate(
            total=Sum('fine_amount')
        )['total'] or 0
        
        # Student engagement
        active_readers = BookIssue.objects.filter(
            is_returned=False
        ).values('student').distinct().count()
        
        total_students = Student.objects.count()
        
        return JsonResponse({
            'success': True,
            'statistics': {
                'total_books': total_books,
                'available_books': available_books,
                'issued_books': issued_books,
                'utilization_rate': round((issued_books / total_books * 100), 2) if total_books > 0 else 0,
                'total_issues': total_issues,
                'active_issues': active_issues,
                'overdue_count': overdue_count,
                'total_fines': float(total_fines),
                'active_readers': active_readers,
                'reader_engagement': round((active_readers / total_students * 100), 2) if total_students > 0 else 0
            }
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)