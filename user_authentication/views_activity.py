# System activity logs view
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.utils import timezone
import csv
import datetime
from .models import AuditTrail
from .utils import get_relevant_activities

def is_staff_or_admin(user):
    """Check if the user is staff or admin"""
    if not user.is_authenticated:
        return False
    try:
        return (hasattr(user, 'profile') and (user.profile.user_type == 'admin' or user.profile.user_type == 'faculty')) or user.is_staff
    except:
        return user.is_staff

@login_required
@user_passes_test(is_staff_or_admin)
def system_activity_logs(request):
    """View for detailed system activity logs with filtering"""
    # Initialize filter variables
    module_filter = request.GET.get('module', '')
    action_filter = request.GET.get('action', '')
    date_from_str = request.GET.get('date_from', '')
    date_to_str = request.GET.get('date_to', '')
    user_filter = request.GET.get('user_filter', '')
    search_query = request.GET.get('search', '')
    export_format = request.GET.get('export', '')
    
    # Parse dates
    date_from = None
    date_to = None
    try:
        if date_from_str:
            date_from = datetime.datetime.strptime(date_from_str, '%Y-%m-%d').date()
        if date_to_str:
            date_to = datetime.datetime.strptime(date_to_str, '%Y-%m-%d').date()
            # Add one day to include the end date
            date_to = datetime.datetime.combine(date_to, datetime.time.max)
    except ValueError:
        # If date parsing fails, use defaults
        date_from = None
        date_to = None
    
    # Default to last 7 days if no dates provided
    if not date_from and not date_to:
        date_to = timezone.now()
        date_from = date_to - datetime.timedelta(days=7)
        date_from = datetime.datetime.combine(date_from.date(), datetime.time.min)
    elif not date_to:
        date_to = timezone.now()
    elif not date_from:
        date_from = datetime.datetime(2000, 1, 1)  # A very old date as default
    
    # Base queryset
    if request.user.profile.user_type == 'admin' or request.user.is_superuser:
        # Admins see all activities
        activities = AuditTrail.objects.all()
    else:
        # Faculty see only relevant activities
        activities = get_relevant_activities(request.user, limit=None)
    
    # Apply filters
    if module_filter:
        activities = activities.filter(module=module_filter)
        
    if action_filter:
        activities = activities.filter(action=action_filter)
        
    if date_from and date_to:
        activities = activities.filter(action_time__range=(date_from, date_to))
        
    if user_filter:
        activities = activities.filter(user_id=user_filter)
        
    if search_query:
        activities = activities.filter(description__icontains=search_query)
    
    # Get available filter options
    available_modules = AuditTrail.objects.values_list('module', flat=True).distinct().order_by('module')
    available_actions = AuditTrail.ACTION_TYPES
    
    if request.user.profile.user_type == 'admin' or request.user.is_superuser:
        available_users = User.objects.filter(is_active=True).order_by('username')
    else:
        # Restrict visible users for faculty
        available_users = User.objects.filter(
            Q(id=request.user.id) |  # Show themselves
            Q(student_profile__course__in=request.user.faculty_profile.courses.all())  # Show students in faculty's courses
        ).distinct().order_by('username')
    
    # Export to CSV if requested
    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="activity_logs_{timezone.now().strftime("%Y%m%d%H%M%S")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'User', 'User Type', 'Action', 'Module', 'Description', 'IP Address'])
        
        for activity in activities:
            user_type = ''
            username = 'Anonymous'
            
            if activity.user:
                username = activity.user.username
                if hasattr(activity.user, 'profile'):
                    user_type = activity.user.profile.user_type
            
            writer.writerow([
                activity.action_time,
                username,
                user_type,
                activity.action,
                activity.module,
                activity.description,
                activity.ip_address or 'N/A'
            ])
            
        return response
    
    # Paginate results
    paginator = Paginator(activities.order_by('-action_time'), 25)  # 25 activities per page
    page = request.GET.get('page')
    
    try:
        activities = paginator.page(page)
    except PageNotAnInteger:
        activities = paginator.page(1)
    except EmptyPage:
        activities = paginator.page(paginator.num_pages)
    
    context = {
        'activities': activities,
        'available_modules': available_modules,
        'available_actions': available_actions,
        'available_users': available_users,
        'selected_module': module_filter,
        'selected_action': action_filter,
        'selected_user': user_filter,
        'search_query': search_query,
        'date_from': date_from,
        'date_to': date_to,
    }
    
    return render(request, 'system_activity_logs.html', context)
