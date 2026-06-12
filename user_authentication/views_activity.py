# System activity logs view
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.core.paginator import Paginator
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
    module_filter = request.GET.get('module', '')
    action_filter = request.GET.get('action', '')
    date_from_str = request.GET.get('date_from', '')
    date_to_str = request.GET.get('date_to', '')
    user_filter = request.GET.get('user_filter', '')
    search_query = request.GET.get('search', '')
    export_format = request.GET.get('export', '')

    profile = getattr(request.user, 'profile', None)
    user_type = getattr(profile, 'user_type', None)
    is_admin_user = request.user.is_superuser or user_type == 'admin'

    if is_admin_user:
        visible_activities = AuditTrail.objects.select_related('user', 'user__profile').all()
    else:
        visible_activities = get_relevant_activities(request.user, limit=None).select_related('user', 'user__profile')

    total_activity_count = visible_activities.count()
    activities = visible_activities

    date_error = ''
    date_from = None
    date_to = None
    if date_from_str:
        try:
            parsed_from = datetime.datetime.strptime(date_from_str, '%Y-%m-%d').date()
            date_from = timezone.make_aware(
                datetime.datetime.combine(parsed_from, datetime.time.min),
                timezone.get_current_timezone()
            )
        except ValueError:
            date_error = 'Invalid start date ignored.'

    if date_to_str:
        try:
            parsed_to = datetime.datetime.strptime(date_to_str, '%Y-%m-%d').date()
            date_to = timezone.make_aware(
                datetime.datetime.combine(parsed_to, datetime.time.max),
                timezone.get_current_timezone()
            )
        except ValueError:
            date_error = 'Invalid end date ignored.'

    if module_filter:
        activities = activities.filter(module=module_filter)

    if action_filter:
        activities = activities.filter(action=action_filter)

    if date_from:
        activities = activities.filter(action_time__gte=date_from)

    if date_to:
        activities = activities.filter(action_time__lte=date_to)

    if user_filter:
        activities = activities.filter(user_id=user_filter)

    if search_query:
        activities = activities.filter(
            Q(description__icontains=search_query) |
            Q(module__icontains=search_query) |
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(ip_address__icontains=search_query)
        )

    available_modules = (
        visible_activities
        .exclude(module='')
        .values_list('module', flat=True)
        .distinct()
        .order_by('module')
    )
    available_actions = AuditTrail.ACTION_TYPES

    if is_admin_user:
        available_users = User.objects.filter(is_active=True).order_by('username')
    elif user_type == 'faculty' and hasattr(request.user, 'faculty_profile'):
        # Restrict visible users for faculty
        available_users = User.objects.filter(
            Q(id=request.user.id) |  # Show themselves
            Q(student_profile__course__in=request.user.faculty_profile.courses.all())  # Show students in faculty's courses
        ).distinct().order_by('username')
    else:
        available_users = User.objects.filter(id=request.user.id)

    filtered_activities = activities.order_by('-action_time')
    filtered_activity_count = filtered_activities.count()
    active_filter_count = sum(
        1 for value in [module_filter, action_filter, date_from_str, date_to_str, user_filter, search_query]
        if value
    )

    query_params = request.GET.copy()
    query_params.pop('page', None)
    query_params.pop('export', None)
    filter_querystring = query_params.urlencode()

    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="activity_logs_{timezone.now().strftime("%Y%m%d%H%M%S")}.csv"'

        writer = csv.writer(response)
        writer.writerow(['Timestamp', 'User', 'User Type', 'Action', 'Module', 'Description', 'IP Address'])

        for activity in filtered_activities:
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

    page = request.GET.get('page')
    paginator = Paginator(filtered_activities, 25)
    activities_page = paginator.get_page(page)

    context = {
        'activities': activities_page,
        'available_modules': available_modules,
        'available_actions': available_actions,
        'available_users': available_users,
        'selected_module': module_filter,
        'selected_action': action_filter,
        'selected_user': user_filter,
        'search_query': search_query,
        'date_from': date_from_str,
        'date_to': date_to_str,
        'date_error': date_error,
        'filter_querystring': filter_querystring,
        'active_filter_count': active_filter_count,
        'filtered_activity_count': filtered_activity_count,
        'total_activity_count': total_activity_count,
        'latest_activity': filtered_activities.first(),
    }

    return render(request, 'system_activity_logs.html', context)
