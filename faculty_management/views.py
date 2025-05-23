from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Faculty
from .forms import FacultyForm, FacultySearchForm
from django.contrib.auth.models import User, Group
from user_authentication.models import UserProfile  # Added import

# Helper function to check if user is admin
def is_admin(user):
    if not user.is_authenticated:
        return False
    try:
        return (hasattr(user, 'profile') and user.profile.user_type == 'admin') or user.is_superuser
    except UserProfile.DoesNotExist:
        return False

@login_required
def faculty_list(request):
    """View to list all faculty members with search and filter options"""
    faculty = Faculty.objects.all()
    form = FacultySearchForm(request.GET)
    
    # Apply filters if the form is valid
    if form.is_valid():
        search_query = form.cleaned_data.get('search_query')
        department_filter = form.cleaned_data.get('department')
        
        if search_query:
            faculty = faculty.filter(
                Q(name__icontains=search_query) | 
                Q(email__icontains=search_query) | 
                Q(faculty_id__icontains=search_query)
            )
        
        if department_filter:
            faculty = faculty.filter(department__icontains=department_filter)
      # Order faculty by ID to avoid UnorderedObjectListWarning
    faculty = faculty.order_by('faculty_id')
    
    # Paginate the results
    paginator = Paginator(faculty, 10)  # Show 10 faculty members per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'total_faculty': faculty.count(),
    }
    
    return render(request, 'faculty_management/faculty_list.html', context)

@login_required
@user_passes_test(is_admin)
def faculty_create(request):
    """View to create a new faculty member"""
    if request.method == 'POST':
        form = FacultyForm(request.POST)
        if form.is_valid():
            # Create user account
            username = form.cleaned_data['email']
            # Generate temporary password
            password = f"faculty{form.cleaned_data['name'][:3].lower()}"
            
            user = User.objects.create_user(
                username=username,
                email=form.cleaned_data['email'],
                password=password,
                first_name=form.cleaned_data['name'].split()[0],
                last_name=' '.join(form.cleaned_data['name'].split()[1:]) if len(form.cleaned_data['name'].split()) > 1 else '',
            )
            
            # Add user to faculty group if it exists
            faculty_group, created = Group.objects.get_or_create(name='Faculty')
            faculty_group.user_set.add(user)
            
            # Set staff status to allow access to admin site
            user.is_staff = True
            user.save()
            
            # Create faculty profile
            faculty = form.save(commit=False)
            faculty.user = user
            faculty.save()
              # Create user profile if it doesn't exist
            from user_authentication.models import UserProfile
            UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'user_type': 'faculty',
                    'phone_number': '',
                    'is_first_login': True  # Ensure the user is required to change password
                }
            )
            
            # Display success message with login credentials
            messages.success(request, 
                f'Faculty {faculty.name} created successfully! ' +
                f'Their username is "{username}" and temporary password is "{password}". ' +
                f'Please inform the faculty member to change their password after first login.'
            )
            return redirect('faculty_detail', pk=faculty.faculty_id)
    else:
        form = FacultyForm()
    
    return render(request, 'faculty_management/faculty_form.html', {'form': form, 'title': 'Add Faculty'})

@login_required
def faculty_detail(request, pk):
    """View to display faculty details"""
    faculty = get_object_or_404(Faculty, faculty_id=pk)
    
    # Only allow access if admin or the faculty member themselves
    if not is_admin(request.user) and request.user != faculty.user:
        messages.error(request, "You don't have permission to view this faculty member's details")
        return redirect('faculty_list')
        
    # Get courses taught by this faculty
    try:
        courses = faculty.courses.all()
    except:
        courses = []
      # Get recent activities for this faculty
    from user_authentication.models import AuditTrail
    from django.utils import timezone
    from datetime import timedelta
    
    # Get activities from the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    
    recent_activities = AuditTrail.objects.filter(
        user=faculty.user,
        action_time__gte=thirty_days_ago
    ).order_by('-action_time')[:10]  # Get the 10 most recent activities
    
    # Add a display date to each activity
    for activity in recent_activities:
        if activity.action_time.date() == today:
            activity.display_date = f"Today at {activity.action_time.strftime('%I:%M %p')}"
        elif activity.action_time.date() == yesterday:
            activity.display_date = f"Yesterday at {activity.action_time.strftime('%I:%M %p')}"
        else:
            activity.display_date = activity.action_time.strftime('%b %d, %Y at %I:%M %p')
        
    context = {
        'faculty': faculty,
        'courses': courses,
        'recent_activities': recent_activities
    }
        
    return render(request, 'faculty_management/faculty_detail.html', context)

@login_required
@user_passes_test(is_admin)
def faculty_update(request, pk):
    """View to update faculty information"""
    faculty = get_object_or_404(Faculty, faculty_id=pk)
    
    if request.method == 'POST':
        form = FacultyForm(request.POST, instance=faculty)
        if form.is_valid():
            # Update user information as well
            faculty.user.email = form.cleaned_data['email']
            faculty.user.first_name = form.cleaned_data['name'].split()[0]
            faculty.user.last_name = ' '.join(form.cleaned_data['name'].split()[1:]) if len(form.cleaned_data['name'].split()) > 1 else ''
            faculty.user.save()
            
            form.save()
            messages.success(request, f'Faculty {faculty.name} updated successfully!')
            return redirect('faculty_detail', pk=faculty.faculty_id)
    else:
        form = FacultyForm(instance=faculty)
    
    return render(request, 'faculty_management/faculty_form.html', {
        'form': form, 
        'title': 'Update Faculty',
        'faculty': faculty
    })

@login_required
@user_passes_test(is_admin)
def faculty_delete(request, pk):
    """View to delete a faculty member"""
    faculty = get_object_or_404(Faculty, faculty_id=pk)
    
    if request.method == 'POST':
        user = faculty.user
        faculty_name = faculty.name
        faculty.delete()
        # Delete associated user account
        user.delete()
        messages.success(request, f'Faculty {faculty_name} deleted successfully!')
        return redirect('faculty_list')
        
    return render(request, 'faculty_management/faculty_confirm_delete.html', {'faculty': faculty})
